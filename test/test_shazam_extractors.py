import unittest

from src import shazam


class ShazamExtractorsTest(unittest.TestCase):
    def test_youtube_long(self):
        self.assertEqual(
            shazam.timestamp_from_extractor(
                "https://www.youtube.com/watch?v=y6120QOlsfU&t=120", "youtube"
            ),
            120,
        )

    def test_youtube_short(self):
        self.assertEqual(
            shazam.timestamp_from_extractor(
                "https://youtu.be/y6120QOlsfU?t=90", "youtube"
            ),
            90,
        )

    def test_soundcloud(self):
        self.assertEqual(
            shazam.timestamp_from_extractor(
                "https://soundcloud.com/euphorichardstylez/euphoricast-59-june-2022"
                "?utm_source=clipboard"
                "&utm_medium=text"
                "&utm_campaign=social_sharing#t=1%3A16%3A48",
                "soundcloud",
            ),
            4608,
        )
