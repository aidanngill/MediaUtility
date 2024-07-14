import pytest

from src import utility


def test_timestamp_valid_s():
    assert utility.timestamp_to_seconds("10") == 10


def test_timestamp_valid_ms():
    assert utility.timestamp_to_seconds("3:45") == 225


def test_timestamp_valid_hms():
    assert utility.timestamp_to_seconds("01:34:21") == 5661


def test_timestamp_invalid():
    with pytest.raises(ValueError):
        utility.timestamp_to_seconds("invalid, this is a string")
