import logging
import logging.handlers
import os
from datetime import datetime

from .bot import bot

logging.getLogger().setLevel(logging.DEBUG)

stream_formatter = logging.Formatter(
    "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_formatter = logging.Formatter(
    "%(created)i/%(name)s/%(levelname)s/%(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(stream_formatter)

file_handler = logging.handlers.TimedRotatingFileHandler(
    filename="./logs/discord.log",
    when="d",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

logging.getLogger().addHandler(stream_handler)
logging.getLogger().addHandler(file_handler)

token = os.getenv("BOT_TOKEN")
assert token != None

bot.run(token, log_handler=None)
