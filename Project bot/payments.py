from aiogram.types import LabeledPrice
from config import STAR_PRICES

def build_invoice(period_key):
    data = STAR_PRICES[period_key]
    return {
        "title": "Подписка Perchance RP",
        "description": f"{data['days']} дней доступа",
        "payload": period_key,
        "currency": "XTR",
        "prices": [LabeledPrice(label="Подписка", amount=data["stars"])]
    }
