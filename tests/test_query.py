import unittest

from usage.query import query


class TestQuery(unittest.TestCase):
    """Tests the query function."""

    def test_no_type(self):
        """Test without the type keyword argument."""
        expected = {
            'field': 'field',
            'op': 'op',
            'value': 'value',
            'type': ''
        }
        q = query(expected['field'], expected['op'], expected['value'])
        for key in expected:
            self.assertEquals(q[key], expected[key])

    def test_with_type(self):
        """Test with the type keyword argument."""
        expected = {
            'field': 'field',
            'op': 'op',
            'value': 'value',
            'type': 'type'
        }
        q = query(
            expected['field'],
            expected['op'],
            expected['value'],
            type=expected['type']
        )
        for key in expected:
            self.assertEquals(q[key], expected[key])
