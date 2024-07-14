from typing import Optional
from urllib import parse

second_multiplier = [
    1,  # seconds
    60,  # minutes
    3_600,  # hours
    86_400,  # days
]


def timestamp_to_seconds(timestamp: str) -> int:
    """Try to convert a timestamp string (e.g., 3:45) to seconds.

    Args:
        timestamp (str): The string we should try to determine a timestamp from.

    Returns:
        The time in seconds.
    """
    split = timestamp.split(":")
    split.reverse()

    split = split[: len(second_multiplier)]

    total_seconds = 0

    for index, item in enumerate(split):
        total_seconds += int(item) * second_multiplier[index]

    return total_seconds


def timestamp_from_extractor(link: str, extractor_key: str) -> Optional[int]:
    """Try to resolve the timestamp from a link and its extractor.

    Args:
        link (str): The provided URL string to find timestamps from.
        extractor_key (str): Which social media we will be extracting the timestamp
            from. Each one may have different methods for storing timestamps in their
            URLs, and so we must differentiate between them to be as accurate as
            possible.

    Returns:
        The timestamp in seconds, or None.
    """
    url_parsed = parse.urlparse(link)

    match extractor_key.lower():
        # For Youtube links the timestamp will be stored in the `?t=` query parameter.
        # Update: They now have an "s" at the end.
        case "youtube":
            url_query_ts = parse.parse_qs(url_parsed.query).get("t")

            if url_query_ts is not None:
                return int(url_query_ts[0].strip("s"))
        # For Soundcloud links they have a URL fragment, e.g., `t=1%3A32` = `t=1:32`.
        case "soundcloud":
            return timestamp_to_seconds(
                parse.unquote(url_parsed.fragment.split("=")[-1])
            )
