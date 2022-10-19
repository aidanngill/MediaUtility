import logging
import os
import time
import zlib
from logging.handlers import TimedRotatingFileHandler


# https://docs.python.org/3/howto/logging-cookbook.html#using-a-rotator-and-namer-to-customize-log-rotation-processing
def namer(name):
    return name + ".gz"


def rotator(source, dest):
    with open(source, "rb") as sf:
        data = sf.read()
        compressed = zlib.compress(data, 9)
        with open(dest, "wb") as df:
            df.write(compressed)
    os.remove(source)


# https://gist.github.com/vernomcrp/18069053fb3cf3807c9e8601eb8016d5
class TimezoneFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            datefmt = datefmt.replace("%f", "%03d" % int(record.msecs))
            datefmt = datefmt.replace("%z", time.strftime("%z"))
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = "%s,%03d" % (t, record.msecs)
        return s


# Logging to the console as a stream.
stream_formatter = logging.Formatter(
    "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

stream_handler = logging.StreamHandler()

stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(stream_formatter)

# Logging more verbosely to a file.
file_formatter = TimezoneFormatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S.%f%z",
)

file_handler = TimedRotatingFileHandler(
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


def setup_logging():
    os.makedirs("./logs", exist_ok=True)

    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
