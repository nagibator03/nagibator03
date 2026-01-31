import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

FREE_MESSAGES = 7

STAR_PRICES = {
    "1d":  {"stars": 100,  "days": 1},
    "3d":  {"stars": 300,  "days": 3},
    "7d":  {"stars": 500,  "days": 7},
    "30d": {"stars": 1000, "days": 30},
}
