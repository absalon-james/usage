import mock
import unittest

from usage.conversions import convert
from usage.conversions.disk_units import bytes_to_gigabytes
from usage.conversions.time_units import seconds_to_hours
from usage.exc import UnknownConversionError


def broken_conversion(value):
    raise Exception("I am broken")
    return value


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


class TestConversion(unittest.TestCase):
    """Tests the conversion plugin loaded."""
    def test_unknown_conversion(self):
        with self.assertRaises(UnknownConversionError):
            convert('shouldntexist', 42)

    @mock.patch(
        'usage.conversions.CONVERSIONS',
        {'broken_conversion': broken_conversion}
    )
    def test_broken_conversion(self):
        self.assertTrue(convert('broken_conversion', 42) is None)
