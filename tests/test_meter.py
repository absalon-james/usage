import datetime
import mock
import unittest

from fakes import FakeSample
from usage.exc import InvalidTimeRangeError
from usage.meter import _cmp_sample
from usage.meter import Meter

now = datetime.datetime.utcnow()
one_hour_ago = now - datetime.timedelta(hours=1)
two_hours_ago = now - datetime.timedelta(hours=2)
three_hours_ago = now - datetime.timedelta(hours=3)
four_hours_ago = now - datetime.timedelta(hours=4)
five_hours_ago = now - datetime.timedelta(hours=5)


class TestCmpSample(unittest.TestCase):

    def test_comparison(self):
        """Tests the sample comparison function used to sort samples."""
        # Test a.resource_id < b.resource_id
        a = FakeSample(resource_id='a')
        b = FakeSample('b')
        self.assertTrue(_cmp_sample(a, b) < 0)

        # Test b.resource_id < a.resource_id
        self.assertTrue(_cmp_sample(b, a) > 0)

        # Test a.resource_id = b.resource_id and a.timestamp = b.timestamp
        b.resource_id = 'a'
        self.assertEquals(_cmp_sample(a, b), 0)

        # Test a.timestamp < b.timestamp
        a.timestamp = 0
        b.timestamp = 1
        self.assertTrue(_cmp_sample(a, b) < 0)

        # Test b.timestamp < a.timestamp
        self.assertTrue(_cmp_sample(b, a) > 0)


class TestMeter(unittest.TestCase):

    def test_init(self):
        """Test the init method."""
        m = Meter('client', 'meter_name')
        self.assertEquals(m.client, 'client')
        self.assertEquals(m.name, 'meter_name')

    def test_count(self):
        """Tests the count method."""
        class FakeStats:
            def __init__(self, count):
                self.count = count

        m = Meter('client', 'meter_name')
        m.client = mock.Mock()
        m.client.statistics.list = mock.Mock()
        m.client.statistics.list.return_value = [FakeStats(10)]
        self.assertEquals(m.count('q'), 10)

        m.client.statistics.list.return_value = []
        self.assertEquals(m.count('q'), 0)

    @mock.patch('usage.meter.Reading')
    def test_read(self, mock_reading):
        """Tests the read method."""
        # Test start > stop
        m = Meter('client', 'meter_name')
        m.client = mock.Mock()

        with self.assertRaises(InvalidTimeRangeError):
            m.read(start=now, stop=one_hour_ago)

        m.count = mock.Mock()
        m.count.return_value = 10

        # Provide samples for separate resources out of order.
        samples = [
            FakeSample(
                resource_id='b',
                counter_volume=2,
                counter_type='gauge',
                timestamp=one_hour_ago.isoformat()
            ),
            FakeSample(
                resource_id='a',
                counter_volume=1,
                counter_type='gauge',
                timestamp=one_hour_ago.isoformat()
            ),
            FakeSample(
                resource_id='a',
                counter_volume=1,
                counter_type='gauge',
                timestamp=two_hours_ago.isoformat()
            ),
            FakeSample(
                resource_id='b',
                counter_volume=2,
                counter_type='gauge',
                timestamp=two_hours_ago.isoformat(),
                resource_metadata={'created_at': four_hours_ago.isoformat()}
            )
        ]
        m.client.samples.list.return_value = samples

        expected_resource_ids = ['a', 'b']
        expected_timestamps = [two_hours_ago, one_hour_ago]
        for i, reading in enumerate(m.read()):
            args, kwargs = mock_reading.call_args
            samples, start, stop = args
            for j, sample in enumerate(samples):
                self.assertEquals(expected_resource_ids[i], sample.resource_id)
                self.assertEquals(expected_timestamps[j], sample.timestamp)
