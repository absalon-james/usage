import datetime
import mock
import unittest

from usage.exc import InvalidTimeRangeError
from usage.exc import UnknownCounterTypeError
from usage.meter import _cmp_sample
from usage.meter import Meter


class FakeSample:
    """Fake sample class for testing."""
    def __init__(self,
                 resource_id=None,
                 timestamp=None,
                 counter_volume=None,
                 resource_metadata=None,
                 counter_name=None,
                 counter_type=None):
        """Set up the fake sample

        :param resource_id: Test resource id. Defaults to 'resource_id'
        :type resource_id: String
        :param timestamp: Test timestamp. Defaults to 0
        :type timestamp: Datetime|Float|Integer
        :param counter_volume: Value of the sample. Defaults to 0
        :type counter_volume: Numeric
        :param resource_metadata: Resource metadata. Defaults to {}.
        :type resource_metadata: Dict
        :param counter_name: Name of the counter. Defaults to 'counter_name'
        :type counter_name: String
        :param counter_type: Type of the counter. Defaults to 'counter_type'
        :type counter_type: String
        """
        self.resource_id = resource_id or 'resource_id'
        self.timestamp = timestamp or 0
        self.counter_volume = counter_volume or 0
        self.resource_metadata = resource_metadata or {}
        self.counter_name = counter_name or 'counter_name'
        self.counter_type = counter_type or 'counter_type'


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

    def test_assume_start(self):
        """Test the assume start method."""
        m = Meter('client', 'meter_name')
        now = datetime.datetime.utcnow()
        two_hours_ago = now - datetime.timedelta(hours=2)
        one_hour_ago = now - datetime.timedelta(hours=1)

        # Assume start with created at < start
        sample = FakeSample(timestamp=now, counter_volume=1)
        sample.resource_metadata = {'created_at': two_hours_ago.isoformat()}
        group = [sample]
        m.assume_start(group, one_hour_ago)
        self.assertEquals(len(group), 2)
        self.assertEquals(group[0].timestamp, one_hour_ago)
        self.assertEquals(group[0].resource_id, group[1].resource_id)
        self.assertEquals(group[0].counter_volume, group[1].counter_volume)
        self.assertFalse(group[0] is group[1])

        # Assume start with created_at > start
        sample = FakeSample(timestamp=now, counter_volume=1)
        sample.resource_metadata = {'created_at': one_hour_ago.isoformat()}
        group = [sample]
        m.assume_start(group, two_hours_ago)
        self.assertEquals(len(group), 2)
        self.assertEquals(group[0].timestamp, one_hour_ago)
        self.assertEquals(group[0].resource_id, group[1].resource_id)
        self.assertEquals(group[0].counter_volume, group[1].counter_volume)
        self.assertFalse(group[0] is group[1])

    def test_assume_stop(self):
        """Test the assume stop method."""
        m = Meter('client', 'meter_name')
        now = datetime.datetime.utcnow()
        two_hours_ago = now - datetime.timedelta(hours=2)
        one_hour_ago = now - datetime.timedelta(hours=1)

        # Test no deleted_at
        sample = FakeSample(timestamp=one_hour_ago, counter_volume=1)
        sample.resource_metadata = {}
        group = [sample]
        m.assume_stop(group, now)
        self.assertEquals(len(group), 2)
        self.assertEquals(group[1].timestamp, now)
        self.assertEquals(group[0].resource_id, group[1].resource_id)
        self.assertEquals(group[0].counter_volume, group[1].counter_volume)
        self.assertFalse(group[0] is group[1])

        # Test deleted_at < stop
        sample = FakeSample(timestamp=two_hours_ago, counter_volume=1)
        sample.resource_metadata = {'deleted_at': one_hour_ago.isoformat()}
        group = [sample]
        m.assume_stop(group, now)
        self.assertEquals(len(group), 2)
        self.assertEquals(group[1].timestamp, one_hour_ago)
        self.assertEquals(group[0].resource_id, group[1].resource_id)
        self.assertEquals(group[0].counter_volume, group[1].counter_volume)
        self.assertFalse(group[0] is group[1])

        # Test deleted_at > stop
        sample = FakeSample(timestamp=two_hours_ago, counter_volume=1)
        sample.resource_metadata = {'deleted_at': now.isoformat()}
        group = [sample]
        m.assume_stop(group, one_hour_ago)
        self.assertEquals(len(group), 2)
        self.assertEquals(group[1].timestamp, one_hour_ago)
        self.assertEquals(group[0].resource_id, group[1].resource_id)
        self.assertEquals(group[0].counter_volume, group[1].counter_volume)
        self.assertFalse(group[0] is group[1])

    def test_gauge(self):
        "''Test the guage method."""
        m = Meter('client', 'meter_name')
        now = datetime.datetime.utcnow()
        one_hour_ago = now - datetime.timedelta(hours=1)
        two_hours_ago = now - datetime.timedelta(hours=2)
        three_hours_ago = now - datetime.timedelta(hours=3)
        four_hours_ago = now - datetime.timedelta(hours=4)

        samples = []
        results = [t for t in m.gauge(samples, three_hours_ago, now)]
        self.assertEquals(len(results), 0)

        samples = [
            FakeSample(
                resource_id='a',
                counter_volume=1,
                timestamp=two_hours_ago,
                resource_metadata={'created_at': four_hours_ago.isoformat()}
            ),
            FakeSample(
                resource_id='a',
                counter_volume=1,
                timestamp=one_hour_ago,
                resource_metadata={'created_at': four_hours_ago.isoformat()}
            ),
            FakeSample(
                resource_id='b',
                counter_volume=2,
                timestamp=two_hours_ago,
                resource_metadata={'created_at': four_hours_ago.isoformat()}
            ),
            FakeSample(
                resource_id='b',
                counter_volume=2,
                timestamp=one_hour_ago,
                resource_metadata={'created_at': four_hours_ago.isoformat()}
            )
        ]

        expected = [3, 6]
        generator = m.gauge(samples, three_hours_ago, now)
        for i, tup in enumerate(generator):
            sample, reading = tup
            self.assertEquals(expected[i], reading)

    def test_cumulative(self):
        """Test the cumulative method..."""
        m = Meter('client', 'meter_name')
        now = datetime.datetime.utcnow()
        two_hours_ago = now - datetime.timedelta(hours=2)

        # Test no samples
        results = [t for t in m.cumulative([], two_hours_ago, now)]
        self.assertEquals(len(results), 0)

        # Test with samples
        samples = [
            FakeSample(
                resource_id='a',
                counter_volume=0,
                timestamp=two_hours_ago
            ),
            FakeSample(
                resource_id='a',
                counter_volume=2,
                timestamp=now
            ),
            FakeSample(
                resource_id='b',
                counter_volume=10,
                timestamp=two_hours_ago
            ),
            FakeSample(
                resource_id='b',
                counter_volume=20,
                timestamp=now
            )
        ]

        expected = [2, 10]
        generator = m.cumulative(samples, two_hours_ago, now)
        for i, tup in enumerate(generator):
            sample, reading = tup
            self.assertEquals(expected[i], reading)

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

    def test_read(self):
        """Tests the read method."""
        # Test start > stop
        now = datetime.datetime.utcnow()
        one_hour_ago = now - datetime.timedelta(hours=1)
        two_hours_ago = now - datetime.timedelta(hours=2)
        three_hours_ago = now - datetime.timedelta(hours=3)
        four_hours_ago = now - datetime.timedelta(hours=4)
        m = Meter('client', 'meter_name')
        m.client = mock.Mock()

        with self.assertRaises(InvalidTimeRangeError):
            m.read(start=now, stop=one_hour_ago)

        m.count = mock.Mock()
        m.count.return_value = 10

        # Unknown counter type
        unknown_samples = [
            FakeSample(
                counter_type='unknown',
                timestamp=one_hour_ago.isoformat()
            )
        ]
        m.client.samples.list.return_value = unknown_samples
        with self.assertRaises(UnknownCounterTypeError):
            m.read(start=one_hour_ago, stop=now)

        # Provide guage samples out of order
        gauge_samples = [
            FakeSample(
                resource_id='b',
                counter_volume=2,
                counter_type='gauge',
                timestamp=one_hour_ago.isoformat(),
                resource_metadata={'created_at': four_hours_ago.isoformat()}
            ),
            FakeSample(
                resource_id='a',
                counter_volume=1,
                counter_type='gauge',
                timestamp=one_hour_ago.isoformat(),
                resource_metadata={'created_at': four_hours_ago.isoformat()}
            ),
            FakeSample(
                resource_id='a',
                counter_volume=1,
                counter_type='gauge',
                timestamp=two_hours_ago.isoformat(),
                resource_metadata={'created_at': four_hours_ago.isoformat()}
            ),
            FakeSample(
                resource_id='b',
                counter_volume=2,
                counter_type='gauge',
                timestamp=two_hours_ago.isoformat(),
                resource_metadata={'created_at': four_hours_ago.isoformat()}
            )
        ]
        m.client.samples.list.return_value = gauge_samples
        expected = [3, 6]
        generator = m.read(start=three_hours_ago, stop=now)
        for i, tup in enumerate(generator):
            sample, reading = tup
            self.assertEquals(expected[i], reading)

        cumulative_samples = [
            FakeSample(
                resource_id='a',
                counter_volume=2,
                counter_type='cumulative',
                timestamp=now.isoformat()
            ),
            FakeSample(
                resource_id='b',
                counter_volume=20,
                counter_type='cumulative',
                timestamp=now.isoformat()
            ),
            FakeSample(
                resource_id='a',
                counter_volume=0,
                counter_type='cumulative',
                timestamp=two_hours_ago.isoformat()
            ),
            FakeSample(
                resource_id='b',
                counter_volume=10,
                counter_type='cumulative',
                timestamp=two_hours_ago.isoformat()
            )
        ]
        m.client.samples.list.return_value = cumulative_samples
        expected = [2, 10]
        generator = m.read(start=two_hours_ago, stop=now)
        for i, tup in enumerate(generator):
            sample, reading = tup
            self.assertEquals(expected[i], reading)
