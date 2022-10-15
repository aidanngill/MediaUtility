import unittest

from src import shazam
from src.exceptions import InvalidLinkException


class ShazamTest(unittest.IsolatedAsyncioTestCase):
    async def test_song_find_invalid(self):
        async def _test_song_find_invalid():
            try:
                await shazam.find_song("invalid, this is a string")
                return False
            except InvalidLinkException:
                return True
        
        self.assertTrue(await _test_song_find_invalid())

    async def test_song_find_by_youtube_valid(self):
        song = await shazam.find_song(
            "https://www.youtube.com/watch?v=y6120QOlsfU",
            use_cache=False,
        )

        self.assertIsNotNone(song)

        self.assertEqual(song["artist"], "Darude")
        self.assertEqual(song["title"], "Sandstorm")
        self.assertEqual(song["album"], "Before the Storm")
    
    async def test_song_by_youtube_valid_no_song(self):
        song = await shazam.find_song(
            "https://www.youtube.com/watch?v=qy882ILYJMM",
            use_cache=False,
        )

        self.assertIsNone(song)

    async def test_song_find_by_soundcloud_valid_ts(self):
        song = await shazam.find_song(
            "https://soundcloud.com/euphorichardstylez/euphoricast-59-june-2022?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing#t=1%3A16%3A48",
            use_cache=False,
        )

        self.assertIsNotNone(song)

        self.assertEqual(song["artist"], "Avi8")
        self.assertEqual(song["title"], "All I Need")
        self.assertEqual(song["album"], "All I Need - Single")

    async def test_song_find_by_soundcloud_valid_ts_explicit(self):
        """ Same timestamp in URL as the other test, but with an explicit
            timestamp that should return another song. """
        song = await shazam.find_song(
            "https://soundcloud.com/euphorichardstylez/euphoricast-59-june-2022?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing#t=1%3A16%3A48",
            timestamp=887,
            use_cache=False,
        )

        self.assertIsNotNone(song)

        self.assertEqual(song["artist"], "Chaoz & Seconds From Space")
        self.assertEqual(song["title"], "Runaway (Extended)")
        self.assertEqual(song["album"], "Runaway - Single")
