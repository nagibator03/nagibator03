import aiosqlite
from datetime import datetime

DB = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            free_messages INTEGER,
            subscription_until TEXT
        )
        """)
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT free_messages, subscription_until FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row:
            await db.execute(
                "INSERT INTO users VALUES (?, ?, ?)",
                (user_id, 7, None)
            )
            await db.commit()
            return 7, None

        return row

async def use_message(user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET free_messages = free_messages - 1 WHERE user_id=?",
            (user_id,)
        )
        await db.commit()

async def set_subscription(user_id, until):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET subscription_until=? WHERE user_id=?",
            (until, user_id)
        )
        await db.commit()
