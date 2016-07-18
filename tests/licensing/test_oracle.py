import mock
import unittest
from usage.licensing.oracle import CountLicenser
from usage.licensing.oracle import HourLicenser


class TestCountLicenser(unittest.TestCase):
    """Test the windows count licenser"""

    costs = {
        'best': {
            'a': 5.0,
            'b': 10.0
        },
        'good': {
            'a': '2.5',
            'b': '5.0'
        }
    }

    @mock.patch('usage.licensing.common.get_domain_name')
    def test_handle_rows(self, mock_get_domain_name):
        mock_get_domain_name.return_value = 'domain'
        rows = [
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'best',
                'image:Oracle Version': 'a'
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'good',
                'image:Oracle Version': 'a'
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'best',
                'image:Oracle Version': 'b'
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'best',
                'image:Oracle Version': 'b'
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'good',
                'image:Oracle Version': 'b'
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'good',
                'image:Oracle Version': 'b'
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'unknown',
                'image:Oracle Version': 'a'
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'good',
                'image:Oracle Version': 'unknown'
            }
        ]
        licenser = CountLicenser(costs=self.costs)
        for row in rows:
            licenser.handle_row(row)

        domain_data = licenser._data['domain']

        edition_unknown_data = domain_data['unknown']
        # Make sure unknown edition version a has a cost of 0
        self.assertEquals(edition_unknown_data['a']['cost'], 0)

        edition_best_data = domain_data['best']
        # Make sure the cost of the best edition version a is 10.0
        self.assertEquals(edition_best_data['a']['cost'], 5.0)
        # Make sure the cost of the best edition version b is  version b is 2.0
        self.assertEquals(edition_best_data['b']['cost'], 20.0)

        edition_good_data = domain_data['good']
        # Make sure cost of good edition version a is 2.5
        self.assertEquals(edition_good_data['a']['cost'], 2.5)
        # Make sure cost of good eidtion version b is 10.0
        self.assertEquals(edition_good_data['b']['cost'], 10.0)
        # Make sure cost of good edition unknown version is 0
        self.assertEquals(edition_good_data['unknown']['cost'], 0.0)


class TestHourLicenser(unittest.TestCase):
    """Test the windows count licenser"""

    costs = {
        'best': {
            'a': 5.0,
            'b': 10.0
        },
        'good': {
            'a': '2.5',
            'b': '5.0'
        }
    }

    @mock.patch('usage.licensing.common.get_domain_name')
    def test_handle_rows(self, mock_get_domain_name):
        mock_get_domain_name.return_value = 'domain'
        rows = [
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'best',
                'image:Oracle Version': 'a',
                'Hours': 1
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'good',
                'image:Oracle Version': 'a',
                'Hours': 1
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'best',
                'image:Oracle Version': 'b',
                'Hours': 1.0
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'best',
                'image:Oracle Version': 'b',
                'Hours': 1.0
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'good',
                'image:Oracle Version': 'b',
                'Hours': 1.0
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'good',
                'image:Oracle Version': 'b',
                'Hours': 1.0
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'unknown',
                'image:Oracle Version': 'a',
                'Hours': 1.0
            },
            {
                'Project Id': 'projectid',
                'image:Oracle Edition': 'good',
                'image:Oracle Version': 'unknown',
                'Hours': 1.0
            }
        ]
        licenser = HourLicenser(costs=self.costs)
        for row in rows:
            licenser.handle_row(row)

        domain_data = licenser._data['domain']

        edition_unknown_data = domain_data['unknown']
        # Make sure unknown edition version a has a cost of 0
        self.assertEquals(edition_unknown_data['a']['cost'], 0)

        edition_best_data = domain_data['best']
        # Make sure the cost of the best edition version a is 10.0
        self.assertEquals(edition_best_data['a']['cost'], 5.0)
        # Make sure the cost of the best edition version b is  version b is 2.0
        self.assertEquals(edition_best_data['b']['cost'], 20.0)

        edition_good_data = domain_data['good']
        # Make sure cost of good edition version a is 2.5
        self.assertEquals(edition_good_data['a']['cost'], 2.5)
        # Make sure cost of good eidtion version b is 10.0
        self.assertEquals(edition_good_data['b']['cost'], 10.0)
        # Make sure cost of good edition unknown version is 0
        self.assertEquals(edition_good_data['unknown']['cost'], 0.0)
