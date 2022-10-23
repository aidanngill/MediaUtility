import os

from .bot import bot
from .logger import setup_logging

setup_logging()

token = os.getenv("BOT_TOKEN")
assert token is not None

bot.run(token, log_handler=None)
