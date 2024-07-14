from src import shazam


def test_youtube_long():
    assert (
        shazam.timestamp_from_extractor(
            "https://www.youtube.com/watch?v=y6120QOlsfU&t=120", "youtube"
        )
        == 120
    )


def test_youtube_long_with_s():
    assert (
        shazam.timestamp_from_extractor(
            "https://www.youtube.com/watch?v=y6120QOlsfU&t=120s", "youtube"
        )
        == 120
    )


def test_youtube_short():
    assert (
        shazam.timestamp_from_extractor("https://youtu.be/y6120QOlsfU?t=90", "youtube")
        == 90
    )


def test_youtube_short_with_s():
    assert (
        shazam.timestamp_from_extractor("https://youtu.be/y6120QOlsfU?t=90s", "youtube")
        == 90
    )


def test_soundcloud():
    assert (
        shazam.timestamp_from_extractor(
            "https://soundcloud.com/euphorichardstylez/euphoricast-59-june-2022"
            "?utm_source=clipboard"
            "&utm_medium=text"
            "&utm_campaign=social_sharing#t=1%3A16%3A48",
            "soundcloud",
        )
        == 4608
    )
