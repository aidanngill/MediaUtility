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

shazam = Shazam()

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
        data_media = await download_media(
            link, os.path.join(path_temp, "%(id)s.%(ext)s")
        )

        # Some extractors have a `&t=` query parameter to denote the timestamp.
        # Prioritise it over the given timestamp, which is usually `None` anyway.
        # TODO: Other services like Soundcloud or whatever.
        if data_media and data_media["extractor"] == "youtube" and timestamp is None:
            query_ts = parse.parse_qs(parse.urlparse(link).query).get("t")

            if query_ts is not None:
                timestamp = int(query_ts[0])

        if timestamp is None:
            timestamp = 0

        # If it is not from a place YoutubeDL supports, manually download it
        # by ourselves. We use the MIME type to guess which extension the file is.
        if not data_media:
            await download_file(link, os.path.join(path_temp, "input-audio.%(ext)s"))

        file_path = os.path.join(path_temp, os.listdir(path_temp)[0])
        file_path_audio = os.path.join(path_temp, "audio.ogg")

        ffmpeg \
            .input(file_path) \
            .filter_("atrim", start=timestamp, end=timestamp + 15) \
            .output(file_path_audio, vn=None) \
            .run(quiet=True)
        
        data_shazam = await shazam.recognize_song(file_path_audio)

        if len(data_shazam["matches"]) == 0:
            return
        
        data_song = song.create(data_shazam)

        if data_media is not None:
            await cache.set_from_info(data_media, data_shazam, timestamp)
        
        return data_song
