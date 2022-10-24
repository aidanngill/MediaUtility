import unittest

from src import shazam
from src.exceptions import InvalidLinkException


class ShazamTest(unittest.IsolatedAsyncioTestCase):
    async def test_song_invalid_url(self):
        """Song link is not a valid link and should fail with an InvalidLinkException."""

        async def _test_song_find_invalid():
            try:
                await shazam.find_song("invalid, this is a string")
                return False
            except InvalidLinkException:
                return True

        self.assertTrue(await _test_song_find_invalid())

    async def test_song_exists(self):
        """Song link is valid, and links to Darude's song "Sandstorm"."""
        song = await shazam.find_song(
            "https://www.youtube.com/watch?v=y6120QOlsfU",
            use_cache=False,
        )

        self.assertIsNotNone(song)

        self.assertEqual(song["artist"], "Darude")
        self.assertEqual(song["title"], "Sandstorm")
        self.assertEqual(song["album"], "Before the Storm")

    async def test_song_none(self):
        """Link is valid, but there is no song."""
        song = await shazam.find_song(
            "https://www.youtube.com/watch?v=qy882ILYJMM",
            use_cache=False,
        )

        self.assertIsNone(song)

    async def test_song_timestamp_url(self):
        """Song is valid, it is a mix and so multiple songs exist. Within the link there
        is a timestamp string. No explicit timestamp is given, and so the function gets
        the song at the link's timestamp, which is Avi8's song "All I Need"."""
        song = await shazam.find_song(
            "https://soundcloud.com/euphorichardstylez/euphoricast-59-june-2022"
            "?utm_source=clipboard"
            "&utm_medium=text"
            "&utm_campaign=social_sharing#t=1%3A16%3A48",
            use_cache=False,
        )

        self.assertIsNotNone(song)

        self.assertEqual(song["artist"], "Avi8")
        self.assertEqual(song["title"], "All I Need")
        self.assertEqual(song["album"], "All I Need - Single")

    async def test_song_timestamp_explicit(self):
        """Same timestamp in URL as the other test, but with an explicit timestamp that
        should return a different song."""
        song = await shazam.find_song(
            "https://soundcloud.com/euphorichardstylez/euphoricast-59-june-2022"
            "?utm_source=clipboard"
            "&utm_medium=text"
            "&utm_campaign=social_sharing#t=1%3A16%3A48",
            time_start=887,
            use_cache=False,
        )

        self.assertIsNotNone(song)

        self.assertEqual(song["artist"], "Chaoz & Seconds From Space")
        self.assertEqual(song["title"], "Runaway (Extended)")
        self.assertEqual(song["album"], "Runaway - Single")

    async def test_song_playlist_index(self):
        """Test finding a song from an item deeper into a playlist."""
        song = await shazam.find_song(
            "https://www.youtube.com/watch?v=QBpF0NTUTnA&list=PL496CFE0819E797DE",
            playlist_index=5,
        )

        self.assertIsNotNone(song)

        self.assertEqual(song["artist"], "Dead or Alive")
        self.assertEqual(song["title"], "Brand New Lover")
        self.assertEqual(song["album"], "'Mad, Bad and Dangerous to Know")
