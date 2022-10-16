import logging
import logging.handlers
import os
import zlib

from .bot import bot

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

stream_formatter = logging.Formatter(
    "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(stream_formatter)

def namer(name):
    return name + ".gz"

def rotator(source, dest):
    with open(source, "rb") as sf:
        data = sf.read()
        compressed = zlib.compress(data, 9)
        with open(dest, "wb") as df:
            df.write(compressed)
    os.remove(source)

file_handler = logging.handlers.TimedRotatingFileHandler(
    filename="./logs/discord.log",
    when="d",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)

file_handler.rotator = rotator
file_handler.namer = namer

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

token = os.getenv("BOT_TOKEN")
assert token != None

bot.run(token, log_handler=None)
