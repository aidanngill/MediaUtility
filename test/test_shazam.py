import pytest

from src import shazam
from src.exceptions import InvalidLinkException

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_song_invalid_url():
    """The link provided is not a valid URI, and should throw an exception."""

    with pytest.raises(InvalidLinkException):
        await shazam.find_song("invalid, this is a string")


@pytest.mark.asyncio
async def test_song_exists():
    """Song link is valid."""
    song = await shazam.find_song(
        "https://www.youtube.com/watch?v=y6120QOlsfU",
        use_cache=False,
    )

    assert song is not None

    assert song["artist"] == "Darude"
    assert song["title"] == "Sandstorm"
    assert song["album"] == "Before the Storm"


@pytest.mark.asyncio
async def test_song_none():
    """Link is valid, but there is no song."""
    song = await shazam.find_song(
        "https://www.youtube.com/watch?v=qy882ILYJMM",
        use_cache=False,
    )

    assert song is None


@pytest.mark.asyncio
async def test_song_timestamp_url():
    """Song is valid, it is a mix and so multiple songs exist. Within the link there
    is a timestamp string. No explicit timestamp is given, and so the function gets
    the song at the link's timestamp."""
    song = await shazam.find_song(
        "https://www.youtube.com/watch?v=wIMSU8otS-g&t=1370s",
        use_cache=False,
    )

    assert song is not None

    assert "Daft Punk" in song["artist"]
    assert "Instant Crush" in song["title"]


@pytest.mark.asyncio
async def test_song_timestamp_explicit():
    """Same timestamp in URL as the other test, but with an explicit timestamp that
    should return a different song."""
    song = await shazam.find_song(
        "https://www.youtube.com/watch?v=wIMSU8otS-g&t=1370s",
        time_start=2560,
        use_cache=False,
    )

    assert song is not None

    assert "Daft Punk" in song["artist"]
    assert "Get Lucky" in song["title"]


@pytest.mark.asyncio
async def test_song_playlist_index():
    """Find two different songs from two different items in a playlist, with the
    same URL."""
    song_one = await shazam.find_song(
        "https://www.youtube.com/watch?v=QBpF0NTUTnA&list=PL496CFE0819E797DE",
        playlist_index=1,
    )

    song_two = await shazam.find_song(
        "https://www.youtube.com/watch?v=QBpF0NTUTnA&list=PL496CFE0819E797DE",
        playlist_index=2,
    )

    assert song_one is not None
    assert song_two is not None

    assert song_one != song_two
