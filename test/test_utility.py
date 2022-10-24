import unittest

from src import utility


class UtilityTest(unittest.TestCase):
    def test_timestamp_valid_s(self):
        self.assertEqual(utility.timestamp_to_seconds("10"), 10)

    def test_timestamp_valid_ms(self):
        self.assertEqual(utility.timestamp_to_seconds("3:45"), 225)

    def test_timestamp_valid_hms(self):
        self.assertEqual(utility.timestamp_to_seconds("01:34:21"), 5661)

    def test_timestamp_invalid(self):
        def _test_timestamp_invalid():
            try:
                utility.timestamp_to_seconds("invalid, this is a string")
                return False
            except ValueError:
                return True

        self.assertTrue(_test_timestamp_invalid())
