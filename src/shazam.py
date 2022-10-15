import asyncio
import mimetypes
import os
from tempfile import TemporaryDirectory
from typing import Optional
from urllib import parse

import aiofiles
import aiohttp
import ffmpeg
import validators
from shazamio import Shazam
from yt_dlp import YoutubeDL

from . import cache
from .api import song
from .exceptions import InvalidLinkException
from .utility import timestamp_to_seconds

_shazam = Shazam()

async def download_file(link: str, path: str) -> None:
    """ Downloads a file from a URL to the given path. """
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            mime = resp.headers.get("Content-Type", "audio/mp3")
            path = path.format(ext=mimetypes.guess_extension(mime))

            async with aiofiles.open(path, "wb") as file:
                await file.write(await resp.content.read())

async def download_media(
    link: str,
    path: str = None,
    _format: str = "worstaudio/worst",
    download: bool = True
) -> Optional[dict]:
    """ Downloads a given piece of media to a path. If no YoutubeDL information
        is found, it is downloaded directly instead. """
    loop = asyncio.get_event_loop()
    opts = {
        "format": _format,
        "quiet": True,
        "outtmpl": path,
    }

    with YoutubeDL(opts) as dl:
        return await loop.run_in_executor(
            None, lambda: dl.extract_info(link, download=download)
        )

async def find_song(
    link: str,
    timestamp: Optional[int] = None
) -> Optional[song.Song]:
    """ Try to find a song given a URL and timestamp. """
    if not validators.url(link): # type: ignore
        raise InvalidLinkException

    with TemporaryDirectory() as path_temp:
        # Download the file to the temporary path.
        data_media = await download_media(link, download=False)

        # Some extractors have a `&t=` query parameter to denote the timestamp.
        # Prioritise it over the given timestamp, which is usually `None` anyway.
        if data_media and timestamp is None:
            url_parsed = parse.urlparse(link)

            if data_media["extractor"] == "youtube":
                url_query_ts = parse.parse_qs(url_parsed.query).get("t")

                if url_query_ts is not None:
                    timestamp = int(url_query_ts[0])
            
            # For Soundcloud links they have a URL fragment, e.g., `t=1%3A32` = `t=1:32`.
            elif data_media["extractor"] == "soundcloud":
                timestamp = timestamp_to_seconds(url_parsed.fragment.split("=")[-1].replace("%3A", ":"))

        # Fallback value if we don't find anything from the extractor.
        if timestamp is None:
            timestamp = 0

        file_path_audio = os.path.join(path_temp, "audio.ogg")

        ffmpeg \
            .input(data_media["url"] if data_media else link, ss=(str(timestamp)), t=15) \
            .output(file_path_audio, vn=None) \
            .run(quiet=True)

        data_shazam = await _shazam.recognize_song(file_path_audio)

        if len(data_shazam["matches"]) == 0:
            return
        
        data_song = song.create(data_shazam)

        if data_media is not None:
            await cache.set_from_info(data_media, data_shazam, timestamp)
        
        return data_song
