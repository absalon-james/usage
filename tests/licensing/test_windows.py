import mock
import unittest
from usage.licensing.windows import CountLicenser
from usage.licensing.windows import HourLicenser


class TestCountLicenser(unittest.TestCase):
    """Test the windows count licenser"""

    costs = {
        'windows': {
            'a': 0.5,
            'b': 1
        }
    }

    @mock.patch('usage.licensing.common.get_domain_name')
    def test_handle_rows(self, mock_get_domain_name):
        mock_get_domain_name.return_value = 'domain'
        rows = [
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'a'
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'a'
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'b'
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'b'
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'c'
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'notwindows',
                'image:OS Version': 'c'
            }
        ]
        licenser = CountLicenser(costs=self.costs)
        for row in rows:
            licenser.handle_row(row)

        domain_data = licenser._data['domain']

        # Make sure the notwindows row was ignored
        self.assertFalse('notwindows' in domain_data)

        windows_data = domain_data['windows']
        # Make sure the cost of the windows version a is 1.0
        self.assertEquals(windows_data['a']['cost'], 1.0)
        # Make sure the cost of the windows version b is 2.0
        self.assertEquals(windows_data['b']['cost'], 2.0)
        # Make sure the cost of the windows version c is 0
        self.assertEquals(windows_data['c']['cost'], 0.0)


class TestHourLicenser(unittest.TestCase):
    """Test the windows count licenser"""

    costs = {
        'windows': {
            'a': 0.5,
            'b': 1
        }
    }

    @mock.patch('usage.licensing.common.get_domain_name')
    def test_handle_rows(self, mock_get_domain_name):
        mock_get_domain_name.return_value = 'domain'
        rows = [
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'a',
                'Hours': 1.0
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'a',
                'Hours': 2.0
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'b',
                'Hours': 1.0
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'b',
                'Hours': 2.0
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'windows',
                'image:OS Version': 'c',
                'Hours': 1.0
            },
            {
                'Project Id': 'projectid',
                'image:OS Distro': 'notwindows',
                'image:OS Version': 'c',
                'Hours': 1.0
            }
        ]
        licenser = HourLicenser(costs=self.costs)
        for row in rows:
            licenser.handle_row(row)

        domain_data = licenser._data['domain']

        # Make sure the notwindows row was ignored
        self.assertFalse('notwindows' in domain_data)

        windows_data = domain_data['windows']
        # Make sure the cost of the windows version a is 1.0
        self.assertEquals(windows_data['a']['cost'], 1.5)
        # Make sure the cost of the windows version b is 2.0
        self.assertEquals(windows_data['b']['cost'], 3.0)
        # Make sure the cost of the windows version c is 0
        self.assertEquals(windows_data['c']['cost'], 0.0)
