import copy
import itertools
import query
import utils

from conversions import seconds_to_hours
from exc import InvalidTimeRangeError
from exc import UnknownCounterTypeError
from log import logging

logger = logging.getLogger('usage.meter')


def _cmp_sample(a, b):
    """Compare two samples.

    First compare the resource ids. Compare the timestamps if the
    resource ids are the same.

    :param a: First sample
    :param b: Second sample
    :return: Result of cmp function.
    :rtype: Integer
    """
    result = cmp(a.resource_id, b.resource_id)
    if result == 0:
        result = cmp(a.timestamp, b.timestamp)
    return result


class Meter:
    """
    Class for interacting with a ceilometer meter.
    """
    def __init__(self, client, name):
        """Init the meter.

        :param client: Ceilometer client
        :type client: ceilometerclient.client
        :param name: Name of the meter
        :type name: String
        """
        self.client = client
        self.name = name

    def assume_start(self, group, start):
        """Create an assumed first datapoint.

        Timestamp will be start if created_at < start
        Timestamp will be created_at if created_at > start

        :param group: List of samples in a group
        :type group: List
        :param start: Start datetime
        :type start: datetime
        """
        fake = copy.copy(group[0])
        created_at = fake.resource_metadata.get('created_at')
        if created_at:
            created_at = utils.parse_datetime(created_at)
            created_at = utils.normalize_time(created_at)
            fake.timestamp = max(start, created_at)
            group.insert(0, fake)

    def assume_stop(self, group, stop):
        """Create an assumed last datapoint.

        Timestamp will be stop if deleted_at > stop
        Timestamp will be deleted at id deleted_at < stop

        :param group:  List of samples in a group
        :type group: List
        :param stop: Stop datetime
        :type stop: datetime
        """
        fake = copy.copy(group[-1])
        deleted_at = fake.resource_metadata.get('deleted_at')
        if deleted_at and deleted_at.lower() != 'none':
            deleted_at = utils.parse_datetime(deleted_at)
            deleted_at = utils.normalize_time(deleted_at)
        else:
            deleted_at = stop
        fake.timestamp = min(stop, deleted_at)
        group.append(fake)

    def gauge(self, samples, start, stop):
        """Compute guage units of time.

        Sort by resource_id

        :param samples: List of samples
        :type samples: List
        :param start: Start date and time
        :type start: datetime
        :param stop: Stop date and time
        :type stop: datetime
        """
        reading = 0.0
        for resource_id, group in itertools.groupby(samples,
                                                    lambda x: x.resource_id):
            # Convert generator to list
            group = list(group)

            # Assume first and last data points
            self.assume_start(group, start)
            self.assume_stop(group, stop)

            group_reading = 0.0
            for i in xrange(1, len(group)):
                group_reading += (
                    (
                        group[i].timestamp -
                        group[i - 1].timestamp
                    ).total_seconds() *
                    (
                        group[i].counter_volume +
                        group[i - 1].counter_volume
                    )
                )

            group_reading = group_reading / 2

            for sample in group:
                logger.debug("\t{} - {} - {} - {}".format(
                    sample.resource_id,
                    sample.counter_name,
                    sample.timestamp,
                    sample.counter_volume
                ))
            reading += group_reading

        # Reading is in unit seconds. Convert to unit hours.
        reading = seconds_to_hours(reading)
        return reading

    def cumulative(self, samples, start, stop):
        """Computes cumulative differences.

        :param samples: List of samples
        :type samples: List
        :param start: Start time
        :type start: datetime
        :param stop: Stop time
        :type stop: datetime
        :return: Cumulative difference
        :rtype: Float
        """
        reading = 0.0
        for resource_id, group in itertools.groupby(samples,
                                                    lambda x: x.resource_id):
            # Convert generator to list
            group = list(group)
            # Compute difference by using first and last datapoints
            difference = group[-1].counter_volume - group[0].counter_volume
            for sample in group:
                logger.debug("\t{} - {} - {} - {}".format(
                    sample.resource_id,
                    sample.counter_name,
                    sample.timestamp,
                    sample.counter_volume
                ))
            reading += difference
        return reading

    def count(self, q):
        """Get a count of samples matching q.

        Since ceilometer does not support sample paging and a default limit of
        100 samples, we need to use stats to count the samples and change the
        limit from 100 the actual number of samples.

        :param q: Listg of filters.
        :type q: List
        :return: Count of samples
        :rtype: Integer
        """
        # Get count of samples
        stats = self.client.statistics.list(meter_name=self.name, q=q,
                                            aggregates=[{'func': 'count'}])
        if not stats:
            return 0
        return stats[0].count

    def read(self, start=None, stop=None, q=None):
        """Read a meter.

        :param start: Start date and time.
        :type start: datetime
        :param stop: Stop date and time.
        :type stop: datetime
        :param q: List of filters excluding timestamp filters
        :type q: List
        :return: Value of reading
        :rtype: Float
        """
        # Default times to month to date
        default_start, default_end = utils.mtd_range()
        if start is None:
            start = default_start
        if stop is None:
            stop = default_end
        if start > stop:
            raise InvalidTimeRangeError(start, stop)

        # Add times to query
        if q is None:
            q = []
        q.append(query.query('timestamp', 'gt', start, 'datetime'))
        q.append(query.query('timestamp', 'le', stop, 'datetime'))

        # Count of samples:
        count = self.count(q)
        logger.debug("{} samples according to statistics.".format(count))
        if not count:
            return 0.0

        # Get samples
        samples = self.client.samples.list(
            meter_name=self.name, q=q, limit=count
        )
        logger.debug(
            "{} samples according to sample-list.".format(len(samples))
        )

        # Convert timestamps from strings to datetime objects
        for s in samples:
            s.timestamp = utils.normalize_time(
                utils.parse_datetime(s.timestamp)
            )

        # Sort by resource id and then timestamps in ascending order
        samples.sort(cmp=_cmp_sample)

        # Determine type of meter
        # For now just use first sample and assume its the same for all
        meter_type = samples[0].counter_type
        if not hasattr(self, meter_type):
            raise UnknownCounterTypeError(meter_type)
        return getattr(self, meter_type)(samples, start, stop)
