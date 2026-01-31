import asyncio
from datetime import datetime, timedelta
import time

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from config import BOT_TOKEN, FREE_MESSAGES, STAR_PRICES
from characters import CHARACTERS
from database import init_db, get_user, use_message, set_subscription
from perchance import send_message
from payments import build_invoice

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

user_state = {}  # user_id -> character_key
last_message_time = {}
perchance_lock = asyncio.Lock()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👩‍🎭 Сменить персонажа", callback_data="change_char")],
        [InlineKeyboardButton(text="⭐ Подписка", callback_data="subscribe")]
    ])

def sub_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 день — 100 ⭐", callback_data="sub_1d")],
        [InlineKeyboardButton(text="3 дня — 300 ⭐", callback_data="sub_3d")],
        [InlineKeyboardButton(text="7 дней — 500 ⭐", callback_data="sub_7d")],
        [InlineKeyboardButton(text="30 дней — 1000 ⭐", callback_data="sub_30d")]
    ])

@dp.message(CommandStart())
async def start(msg: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=c["name"], callback_data=k)]
            for k, c in CHARACTERS.items()
        ]
    )
    await msg.answer("Выбери персонажа:", reply_markup=kb)

@dp.callback_query(F.data.startswith("sub_"))
async def buy_sub(cb):
    key = cb.data.replace("sub_", "")
    invoice = build_invoice(key)
    await bot.send_invoice(
        chat_id=cb.from_user.id,
        **invoice,
        provider_token=""
    )

@dp.message(F.successful_payment)
async def payment_success(msg: Message):
    key = msg.successful_payment.invoice_payload
    days = STAR_PRICES[key]["days"]

    until = datetime.utcnow() + timedelta(days=days)
    await set_subscription(msg.from_user.id, until.isoformat())

    await msg.answer("✅ Подписка активирована! Приятного общения 💬",
                     reply_markup=main_menu())

@dp.callback_query()
async def choose_character(cb):
    if cb.data in CHARACTERS:
        user_state[cb.from_user.id] = cb.data
        await cb.message.answer("Ты можешь писать сообщение 💬")
    elif cb.data == "change_char":
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=c["name"], callback_data=k)]
                for k, c in CHARACTERS.items()
            ]
        )
        await cb.message.answer("Выбери персонажа:", reply_markup=kb)
    elif cb.data == "subscribe":
        await cb.message.answer("Выберите тариф:", reply_markup=sub_menu())

@dp.message(F.text)
async def chat(msg: Message):
    user_id = msg.from_user.id
    char_key = user_state.get(user_id)

    if not char_key:
        await msg.answer("Сначала выбери персонажа.")
        return

    now_time = time.time()
    last = last_message_time.get(user_id, 0)
    if now_time - last < 4:
        await msg.answer("⏳ Подожди пару секунд…")
        return
    last_message_time[user_id] = now_time

    free, sub_until = await get_user(user_id)
    now = datetime.utcnow()

    if not sub_until or datetime.fromisoformat(sub_until) < now:
        if free <= 0:
            await msg.answer("❌ Лимит исчерпан. Купи подписку ⭐",
                             reply_markup=sub_menu())
            return
        await use_message(user_id)

    char = CHARACTERS[char_key]
    async with perchance_lock:
        reply = await send_message(user_id, char["url"], msg.text)

    await msg.answer(reply, reply_markup=main_menu())

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
