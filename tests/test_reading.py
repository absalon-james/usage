import datetime
import mock
import unittest

from fakes import FakeSample
from usage.exc import UnknownCounterTypeError
from usage.reading import Reading

now = datetime.datetime.utcnow()
one_hour_ago = now - datetime.timedelta(hours=1)
two_hours_ago = now - datetime.timedelta(hours=2)
three_hours_ago = now - datetime.timedelta(hours=3)
four_hours_ago = now - datetime.timedelta(hours=4)
five_hours_ago = now - datetime.timedelta(hours=5)


class TestReading(unittest.TestCase):
    """Tests the reading class."""
    def test_init(self):
        r = Reading([], 'start', 'stop')
        self.assertEquals(r.start, 'start')
        self.assertEquals(r.stop, 'stop')

    def test_split_samples(self):
        # Test Samples with before, during, and after
        samples = [
            FakeSample(timestamp=five_hours_ago),
            FakeSample(timestamp=four_hours_ago),
            FakeSample(timestamp=three_hours_ago),
            FakeSample(timestamp=two_hours_ago),
            FakeSample(timestamp=one_hour_ago),
            FakeSample(timestamp=now)
        ]
        r = Reading(samples, four_hours_ago, one_hour_ago)
        self.assertEquals(4, len(r.samples))
        # Check during samples and their order
        expected_timestamps = [
            four_hours_ago,
            three_hours_ago,
            two_hours_ago,
            one_hour_ago
        ]
        for i, sample in enumerate(r.samples):
            self.assertEquals(expected_timestamps[i], sample.timestamp)
        # Resource should exist before start
        self.assertTrue(r.resource_existed_before())
        # Resource should exist after stop
        self.assertTrue(r.resource_existed_after())

        # Test no samples
        samples = []
        r = Reading(samples, four_hours_ago, one_hour_ago)
        self.assertEquals(0, len(r.samples))
        self.assertFalse(r.resource_existed_before())
        self.assertFalse(r.resource_existed_after())

        # Test no prior samples
        samples = [
            FakeSample(timestamp=three_hours_ago),
            FakeSample(timestamp=now)
        ]
        r = Reading(samples, four_hours_ago, one_hour_ago)
        self.assertEquals(1, len(r.samples))
        self.assertEquals(three_hours_ago, r.samples[0].timestamp)
        self.assertFalse(r.resource_existed_before())
        self.assertTrue(r.resource_existed_after())

        # Test no post samples
        samples = [
            FakeSample(timestamp=five_hours_ago),
            FakeSample(timestamp=three_hours_ago)
        ]
        r = Reading(samples, four_hours_ago, two_hours_ago)
        self.assertEquals(1, len(r.samples))
        self.assertEquals(three_hours_ago, r.samples[0].timestamp)
        self.assertTrue(r.resource_existed_before())
        self.assertFalse(r.resource_existed_after())

    def test_usage_start(self):
        # Test usage start no prior samples
        samples = [FakeSample(timestamp=three_hours_ago)]
        r = Reading(samples, four_hours_ago, now)
        self.assertEquals(three_hours_ago, r.usage_start)

        # Test usage start with prior samples
        samples = [
            FakeSample(timestamp=five_hours_ago),
            FakeSample(timestamp=three_hours_ago)
        ]
        r = Reading(samples, four_hours_ago, now)
        self.assertEquals(four_hours_ago, r.usage_start)

        # Test usage start with no samples
        r = Reading([], four_hours_ago, two_hours_ago)
        self.assertTrue(r.usage_start is None)

    def test_usage_stop(self):
        # Test usage stop with no post samples
        samples = [FakeSample(timestamp=three_hours_ago)]
        r = Reading(samples, four_hours_ago, two_hours_ago)
        self.assertEquals(three_hours_ago, r.usage_stop)

        # Test usage stop with post samples
        samples = [
            FakeSample(timestamp=three_hours_ago),
            FakeSample(timestamp=one_hour_ago)
        ]
        r = Reading(samples, four_hours_ago, two_hours_ago)
        self.assertEquals(two_hours_ago, r.usage_stop)

        # Test usage stop with no samples
        r = Reading([], four_hours_ago, two_hours_ago)
        self.assertTrue(r.usage_stop is None)

    def test_resource_id(self):
        samples = [FakeSample(timestamp=one_hour_ago)]
        r = Reading(samples, two_hours_ago, now)
        self.assertEquals(r.resource_id, 'resource_id')

    def test_meter_name(self):
        samples = [FakeSample(timestamp=one_hour_ago)]
        r = Reading(samples, two_hours_ago, now)
        self.assertEquals(r.meter_name, 'meter')

    def test_project_id(self):
        samples = [FakeSample(timestamp=one_hour_ago)]
        r = Reading(samples, two_hours_ago, now)
        self.assertEquals(r.project_id, 'project_id')

    def test_no_samples_reading(self):
        r = Reading([], one_hour_ago, now)
        self.assertTrue(r.value is None)

    def test_unknown_meter(self):
        samples = [FakeSample(counter_type='unknown', timestamp=two_hours_ago)]
        with self.assertRaises(UnknownCounterTypeError):
            Reading(samples, two_hours_ago, now)

    def test_guage_reading(self):
        # Test no post/pre samples
        samples = [
            FakeSample(
                counter_volume=1,
                timestamp=three_hours_ago
            ),
            FakeSample(
                counter_volume=1,
                timestamp=two_hours_ago
            )
        ]
        r = Reading(samples, four_hours_ago, one_hour_ago)
        self.assertEquals(r.value, 1.0)

        # Test with pre/post samples
        samples = [
            FakeSample(
                counter_volume=1,
                timestamp=five_hours_ago
            ),
            FakeSample(
                counter_volume=1,
                timestamp=three_hours_ago
            ),
            FakeSample(
                counter_volume=1,
                timestamp=two_hours_ago
            ),
            FakeSample(
                counter_volume=1,
                timestamp=now
            )
        ]
        r = Reading(samples, four_hours_ago, one_hour_ago)
        self.assertEquals(r.value, 3.0)

    def test_cumulative_reading(self):
        # Test with both pre and post samples
        samples = [
            FakeSample(
                counter_type='cumulative',
                counter_volume=1,
                timestamp=five_hours_ago
            ),
            FakeSample(
                counter_type='cumulative',
                counter_volume=2,
                timestamp=four_hours_ago
            ),
            FakeSample(
                counter_type='cumulative',
                counter_volume=3,
                timestamp=three_hours_ago
            ),
            FakeSample(
                counter_type='cumulative',
                counter_volume=4,
                timestamp=two_hours_ago
            ),
            FakeSample(
                counter_type='cumulative',
                counter_volume=5,
                timestamp=one_hour_ago
            )
        ]
        r = Reading(samples, four_hours_ago, two_hours_ago)
        self.assertEquals(r.value, 4 - 2)

    def test_metdata(self):
        # Test no samples:
        samples = []
        r = Reading(samples, five_hours_ago, now)
        self.assertTrue(r.metadata is None)

        # Test samples with no status fields in resource metadata
        samples = [
            FakeSample(
                timestamp=three_hours_ago,
                resource_metadata={'test': 'first'}
            ),
            FakeSample(
                timestamp=two_hours_ago,
                resource_metadata={'test': 'middle'}
            ),
            FakeSample(
                timestamp=two_hours_ago,
                resource_metadata={'test': 'last'}
            )
        ]
        r = Reading(samples, five_hours_ago, now)
        self.assertEquals(r.metadata['test'], 'last')

        # Test samples with status fields.
        # Last sample active using key 'state'
        samples = [
            FakeSample(
                timestamp=three_hours_ago,
                resource_metadata={
                    'test': 'first',
                    'state': 'active'
                }
            ),
            FakeSample(
                timestamp=two_hours_ago,
                resource_metadata={
                    'test': 'middle',
                    'state': 'resized'
                }
            ),
            FakeSample(
                timestamp=two_hours_ago,
                resource_metadata={
                    'test': 'last',
                    'state': 'active'
                }
            )
        ]
        r = Reading(samples, five_hours_ago, now)
        self.assertEquals(r.metadata['test'], 'last')

        # Test samples with status fields.
        # First sample active using key 'status'
        samples = [
            FakeSample(
                timestamp=three_hours_ago,
                resource_metadata={
                    'test': 'first',
                    'status': 'active'
                }
            ),
            FakeSample(
                timestamp=two_hours_ago,
                resource_metadata={
                    'test': 'middle',
                    'status': 'deleting'
                }
            ),
            FakeSample(
                timestamp=one_hour_ago,
                resource_metadata={
                    'test': 'last',
                    'status': 'deleted'
                }
            )
        ]
        r = Reading(samples, five_hours_ago, now)
        self.assertEquals(r.metadata['test'], 'first')

        # Test all samples deleted using mixed status keys
        samples = [
            FakeSample(
                timestamp=three_hours_ago,
                resource_metadata={
                    'test': 'first',
                    'status': 'deleting'
                }
            ),
            FakeSample(
                timestamp=two_hours_ago,
                resource_metadata={
                    'test': 'middle',
                    'state': 'deleting'
                }
            ),
            FakeSample(
                timestamp=one_hour_ago,
                resource_metadata={
                    'test': 'last',
                    'status': 'deleted'
                }
            )
        ]
        r = Reading(samples, five_hours_ago, now)
        self.assertEquals(r.metadata['test'], 'last')

    @mock.patch('usage.reading.convert', return_value='converted')
    def test_convert(self, mock_convert):
        samples = [
            FakeSample(timestamp=three_hours_ago, counter_volume=1),
            FakeSample(timestamp=two_hours_ago, counter_volume=1)
        ]
        r = Reading(samples, four_hours_ago, now)
        self.assertEquals(r.value, 1.0)
        r.convert('some_conversion')
        self.assertEquals(r.value, 'converted')
