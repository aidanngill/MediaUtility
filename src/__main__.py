import os

from .bot import bot

token = os.getenv("BOT_TOKEN")
assert token != None

bot.run(token, log_handler=None)
