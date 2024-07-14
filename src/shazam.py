import asyncio
import mimetypes
import os
from tempfile import TemporaryDirectory
from typing import Optional
import logging

import aiofiles
import aiohttp
import ffmpeg
import validators
from shazamio import Shazam
from yt_dlp import YoutubeDL

from . import cache
from .api import song
from .exceptions import InvalidLinkException
from .utility import timestamp_from_extractor

_shazam = Shazam()

log = logging.getLogger(__name__)


async def download_file(link: str, output_path: str) -> None:
    """Downloads a file from a URL to the given path.

    Args:
        link (str): Where to download the media from. In this case it will be downloaded
            directly.

    Returns:
        None.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            mime = resp.headers.get("Content-Type", "audio/mp3")
            path = output_path.format(ext=mimetypes.guess_extension(mime))

            async with aiofiles.open(path, "wb") as file:
                await file.write(await resp.content.read())


async def download_media(
    link: str,
    output_path: Optional[str] = None,
    file_format: Optional[str] = None,
    playlist_index: int = 1,
    should_download: bool = True,
) -> Optional[dict]:
    """Downloads a given piece of media to a path. If no YoutubeDL information is found,
        it is downloaded directly instead.

    Args:
        link (str): Where to download the media from. Can generally be any social media
            or direct media link.
        output_path (str): Where to save the file to. Will use YoutubeDL's output
            template as described in the following link.
            https://github.com/ytdl-org/youtube-dl/blob/master/README.md#output-template
        file_format (str): The desired format to download the media as. Formats are
            available at the following link.
            https://github.com/ytdl-org/youtube-dl/blob/master/README.md#format-selection
        playlist_index (int): For playlists (such as Instagram posts with multiple
            videos or pictures), which one should be downloaded.
        should_download (bool): Whether the file should be downloaded alongside getting
            the JSON data.

    Returns:
        Any JSON data that YoutubeDL is able to find, can also be None.
    """
    loop = asyncio.get_event_loop()
    opts = {
        "quiet": True,
        "outtmpl": output_path,
        "playlist_items": str(playlist_index),
    }

    if file_format:
        opts["format"] = file_format

    with YoutubeDL(opts) as dl:
        data = await loop.run_in_executor(
            None, lambda: dl.extract_info(link, download=should_download)
        )

        if data is None:
            return

        if data.get("entries"):
            return data["entries"][0]

        return data


async def find_song(
    link: str,
    time_start: Optional[int] = None,
    time_duration: int = 15,
    playlist_index: int = 1,
    use_cache: bool = True,
) -> Optional[song.Song]:
    """Try to find a song from the given media.

    Args:
        link (str): Where to download the media from. Can generally be any social media
            or direct media link.
        time_start (int): The time at which we should search for a song at, in seconds.
        time_duration (int): How long the sample sent to Shazam should be, in seconds.
        playlist_index (int): For playlists (such as Instagram posts with multiple
            videos or pictures), which one should be downloaded.
        use_cache (bool): Whether we should look in the cache for previous searches,
            provided the same extractor, ID, and start time.

    Returns:
        Data about the song, or None.
    """
    if not validators.url(link):  # type: ignore
        raise InvalidLinkException

    loop = asyncio.get_event_loop()

    with TemporaryDirectory() as path_temp:
        # Download the file to the temporary path.
        data_media = await download_media(
            link,
            file_format="worstaudio/worst",
            playlist_index=playlist_index,
            should_download=False,
        )

        # Some extractors have a `&t=` query parameter to denote the timestamp.
        # If we're not provided an explicit timestamp, try to get it from here
        # instead.
        if data_media and time_start is None:
            time_start = timestamp_from_extractor(link, data_media["extractor_key"])

        # Fallback value if we don't find anything from the extractor.
        if time_start is None:
            time_start = 0

        # Check for existing cache in Redis.
        if data_media and use_cache:
            maybe_song = await cache.get_from_info(data_media, time_start)

            if maybe_song is not None:
                if len(maybe_song.keys()) == 0:
                    return

                return maybe_song

        path_audio_input = os.path.join(path_temp, "input.ogg")
        path_audio_output = os.path.join(path_temp, "output.ogg")

        # Some services don't allow chunked downloads as required later by the
        # `ss` argument of the `ffmpeg` command.
        should_download = "tiktok" in link

        if should_download:
            await download_media(
                link,
                output_path=path_audio_input,
                file_format="worstaudio/worst",
                playlist_index=playlist_index,
            )
        else:
            path_audio_input = data_media["url"] if data_media else link

        def _download_media():
            cmd = ffmpeg.input(
                filename=path_audio_input,
                ss=(str(time_start)),
                t=time_duration,
            ).output(path_audio_output, vn=None)
            
            log.debug(" ".join(cmd.compile()))

            cmd.run(quiet=True)

        await loop.run_in_executor(None, lambda: _download_media())

        data_shazam = await _shazam.recognize(path_audio_output)

        if data_media and use_cache and len(data_shazam["matches"]) == 0:
            await cache.set_empty_from_info(data_media, time_start)
            return

        data_song = song.create(data_shazam)

        if use_cache and data_media is not None:
            await cache.set_from_info(data_media, data_shazam, time_start)

        return data_song
