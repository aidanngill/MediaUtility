import json
import logging
import os
from typing import Optional

from redis import asyncio as aioredis
from redis.exceptions import ConnectionError

from .api import song

log = logging.getLogger(__name__)

async def __create_connection() -> aioredis.Redis:
    conn = aioredis.from_url(os.getenv("REDIS_HOST", "redis://localhost"))
    await conn.ping()

    return conn

async def set_empty_from_info(media_info: dict, scan_start: int = 0) -> None:
    """
    Add any unidentified song to the Redis cache.

    :param dict media_info: Data we get from `YoutubeDL.extract_info`.
    :param int scan_start: Timestamp (in seconds) at which the audio was scanned from.
    """
    try:
        redis = await __create_connection()
    except ConnectionError:
        log.warning("Failed to connect to Redis host")
        return

    key_format = [media_info["extractor"], media_info["id"], str(scan_start)]
    key_string = "-".join(key_format)

    await redis.set(key_string, "{}")

async def set_from_info(media_info: dict, song_info: dict, scan_start: int = 0) -> None:
    """
    Add any identified song to the Redis cache.

    :param dict media_info: Data we get from `YoutubeDL.extract_info`.
    :param dict song_info: Data we get from `Shazam.recognize_song`.
    :param int scan_start: Timestamp (in seconds) at which the audio was scanned from.
    """
    try:
        redis = await __create_connection()
    except ConnectionError:
        log.warning("Failed to connect to Redis host")
        return

    key_format = [media_info["extractor"], media_info["id"], str(scan_start)]
    key_string = "-".join(key_format)

    value_data = song.create(song_info)
    value_encoded = json.dumps(value_data, separators=(',', ':'))

    await redis.set(key_string, value_encoded)

async def get_from_info(media_info: dict, scan_start: int = 0) -> Optional[song.Song]:
    """
    Get any identified song from the Redis cache.

    :param dict media_info: Data we get from `YoutubeDL.extract_info`.
    :param int scan_start: Timestamp (in seconds) at which the audio was scanned from.

    :rtype: str | None
    :return: Any identified songs, or nothing.
    """
    try:
        redis = await __create_connection()
    except ConnectionError:
        log.warning("Failed to connect to Redis host")
        return

    key_format = [media_info["extractor"], media_info["id"], str(scan_start)]
    key_string = "-".join(key_format)

    data: bytes = await redis.get(key_string)

    if data is None:
        return

    data_decoded = json.loads(data.decode("utf-8"))

    return song.Song(**data_decoded)
