import mock
import unittest

from usage.conversions import convert
from usage.conversions.disk_units import bytes_to_gigabytes
from usage.conversions.disk_units import megabytes_to_gigabytes
from usage.conversions.time_units import hours_to_days
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


class TestMegabytesToGigabytes(unittest.TestCase):
    """Test megabytes_to_gigabytes function."""

    def test_nonzero(self):
        """Tests a nonzero input."""
        mb = 1024.0
        self.assertEquals(megabytes_to_gigabytes(mb), 1.0)

    def test_zero(self):
        """Tests a zero input."""
        self.assertEquals(megabytes_to_gigabytes(0), 0)


class TestHoursToDays(unittest.TestCase):
    """Test hours_to_days functions."""

    def test_nonzero(self):
        self.assertEquals(hours_to_days(24), 1.0)
        self.assertEquals(hours_to_days(12), 0.5)

    def test_zero(self):
        self.assertEquals(hours_to_days(0), 0)


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
