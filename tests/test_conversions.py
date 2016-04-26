import unittest

from usage.conversions import bytes_to_gigabytes
from usage.conversions import seconds_to_hours


class TestBytesToGigabytes(unittest.TestCase):
    """Test bytes_to_gigabytes function"""

    def test_nonzero(self):
        """Test a nonzero input."""
        bytes = 1024 * 1024 * 1024
        self.assertEquals(bytes_to_gigabytes(bytes), 1.0)

    def test_zero(self):
        """Test a zero input."""
        self.assertEquals(bytes_to_gigabytes(0), 0)


class TestSecondsToHours(unittest.TestCase):
    """Tests seconds to hours function."""

    def test_nonzero(self):
        """Test a nonzero input."""
        self.assertEquals(seconds_to_hours(3600), 1.0)

    def test_zero(self):
        """Tests a zero input."""
        self.assertEquals(seconds_to_hours(0), 0)
