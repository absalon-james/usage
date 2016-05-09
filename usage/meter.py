import datetime
import itertools
import query
import utils

from exc import InvalidTimeRangeError
from log import logging
from reading import Reading

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

        # Extra time is 4 hours. 4 * 60 * 60 = 14400
        self._extra_time = datetime.timedelta(seconds=14400)

    def last_non_deleted_sample(self, group):
        """Get last sample that is not in deleted or deleting.

        Starts at the end of the group and looks backward for the first sample
        that is not in a deleted or deleting status.

        If a sample cannot be found, just return the last sample.

        :param group: List of samples that are already sorted by timestamp.
        :type group: List
        :returns: Last non deleted status sample.
        :rtype: sample
        """
        deleted_status = set(['deleted', 'deleting'])
        for i in xrange(len(group) - 1, -1, -1):
            if group[i].resource_metadata.get('status') not in deleted_status:
                return group[i]
        return group[-1]

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

    def _reading_generator(self, samples, start, stop):
        """Yields one reading at a time.

        Samples are grouped by resource id(already sorted by resource id)
        and then used to create a reading object.

        :param samples: List of samples sorted by resource_id and timestamp.
        :type samples: List
        :param start: Reading start time
        :type start: Datetime
        :param stop: Reading stop time
        :type stop: Datetime
        :yields: Reading objects
        """
        # Yield a reading for each resource/meter pair
        for _, g in itertools.groupby(samples, lambda x: x.resource_id):
            yield Reading(list(g), start, stop)

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
        default_start, default_stop = utils.mtd_range()
        if not start:
            start = default_start
        if not stop:
            stop = default_stop
        logger.info("Start: {}".format(start))
        logger.info("Stop:  {}".format(stop))
        logger.info("Meter name: {}".format(self.name))
        if start > stop:
            raise InvalidTimeRangeError(start, stop)

        # Add times to query. times are +- the extra time.
        q = q or []
        q.append(query.query(
            'timestamp', 'gt', start - self._extra_time, 'datetime'
        ))
        q.append(query.query(
            'timestamp', 'le', stop + self._extra_time, 'datetime'
        ))

        # Count of samples:
        count = self.count(q)
        logger.debug("{} samples according to statistics.".format(count))
        if not count:
            return []

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

        # Return generator
        return self._reading_generator(samples, start, stop)
