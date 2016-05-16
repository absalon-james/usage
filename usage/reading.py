import copy
from exc import UnknownCounterTypeError
from log import logging

from conversions import convert
from conversions.time_units import seconds_to_hours


ALLOWED_METER_TYPES = set(['gauge', 'cumulative', 'delta'])
logger = logging.getLogger('usage.reading')


class Reading:
    """Models a reading of a meter."""

    def __init__(self, samples, start, stop):
        """Init the reading.

        :param samples: List of samples sorted by timestamp.
        :type samples: List
        :param start: Starting datetime.
        :type start: Datetime
        :param stop: Stopping datetime.
        :type stop: Datetime
        """
        self.start = start
        self.stop = stop
        self._split_samples(samples)
        self._calculate()
        self._set_metadata()

    def _split_samples(self, samples):
        """Split samples into three buckets.

        One for samples prior to start.
        One for samples between start and stop.
        One for samples after stop.

        :param samples: List of samples sorted by timestamp
        :type samples: List
        """
        # Potentially a long running loop. Use local variables where possible.
        prior_samples = []
        during_samples = []
        post_samples = []
        start = self.start
        stop = self.stop

        for sample in samples:
            logger.debug("{} - {} - {} - {} - {}".format(
                sample.resource_id,
                sample.message_id,
                sample.timestamp,
                sample.counter_name,
                sample.counter_volume
            ))
            # Check common case first
            if sample.timestamp >= start and sample.timestamp <= stop:
                during_samples.append(sample)
                continue

            # Second most common case
            if sample.timestamp < start:
                prior_samples.append(sample)
                continue

            # Must be a post sample
            post_samples.append(sample)

        self._prior_samples = prior_samples
        self._during_samples = during_samples
        self._post_samples = post_samples

    def resource_existed_before(self):
        """Determine if resource existed before self.start.

        :returns: The length of prior samples > 0
        :rtype: Bool
        """
        return len(self._prior_samples) > 0

    def resource_existed_after(self):
        """Determine if resource existed after self.stop.

        :returns: The lenght of post samples > 0
        """
        return len(self._post_samples) > 0

    @property
    def project_id(self):
        """Get the project id for the reading.

        :returns: Project id
        :rtype: String
        """
        return self._during_samples[0].project_id

    @property
    def resource_id(self):
        """Get the resource id for the reading.

        :returns: Resource id
        :rtype: String
        """
        return self._during_samples[0].resource_id

    @property
    def usage_start(self):
        """Get the usage start time.

        Will be either self.start or the first during sample timestamp.

        :returns: Usage start time
        :rtype: Datetime|None
        """
        if not self._during_samples:
            return None
        if self.resource_existed_before():
            return self.start
        return self._during_samples[0].timestamp

    @property
    def usage_stop(self):
        """Get the usage stop time.

        Will be either self.stop or the last during sample timestamp.

        :returns: Usage stop time
        :rtype: Datetime|None
        """
        if not self._during_samples:
            return None
        if self.resource_existed_after():
            return self.stop
        return self._during_samples[-1].timestamp

    @property
    def samples(self):
        """Gets during samples.

        :returns: List of samples between start and stop
        :rtype: List
        """
        return self._during_samples

    @property
    def meter_name(self):
        """Get the name of the meter.

        :returns: Name of the meter
        :rtype: String
        """
        if not self._during_samples:
            return None
        return self._during_samples[-1].meter

    @property
    def meter_type(self):
        """Get the type of meter.

        :returns: Type of meter
        :rtype: String
        """
        if not self._during_samples:
            return None
        return self._during_samples[0].counter_type

    def _assume_ends(self):
        """Correct the ends of the sampling.

        We prepend an assumed sample to the end and beginning of the samples
        based on usage start and stop times. This allows us to get a more
        reading where samples do not occur close to the end of the biliing
        start and stop times.

        This is only useful for gauge type meters.

        If the first sample is the usage start time and not the billing start
        time, then we are adding another point at the same time and it has no
        effect on the value.

        If there are samples prior to the billing start time, then the
        resource existed prior to the billing start time and it is safe
        to assume a sample at the billing start time.

        Likewise for the end of the samples.
        """
        # Prepend usage start
        assumed_start = copy.copy(self._during_samples[0])
        assumed_start.timestamp = self.usage_start
        self._during_samples.insert(0, assumed_start)

        # Append usage stop
        assumed_stop = copy.copy(self._during_samples[-1])
        assumed_stop .timestamp = self.usage_stop
        self._during_samples.append(assumed_stop)

    def _gauge(self):
        """Compute gauge reading as guage units of time.

        Performs a trapezoidal approximation of the gauge time series data.
        """
        value = 0.0
        self._assume_ends()
        samples = self._during_samples

        for i in xrange(1, len(self._during_samples)):
            value += (
                (
                    samples[i].timestamp -
                    samples[i - 1].timestamp
                ).total_seconds() *
                (
                    samples[i].counter_volume +
                    samples[i - 1].counter_volume
                )
            )
        value = value / 2
        # Value is in unit seconds. convert to unit hours.
        self.value = seconds_to_hours(value)

        # Remove assumed start and stop
        self._during_samples.pop(0)
        self._during_samples.pop()

    def _cumulative(self):
        """Compute cumulative reading.

        Cumulative meters are counters. Just need to subtract the
        first value from the last value.
        """
        self.value = \
            self._during_samples[-1].counter_volume - \
            self._during_samples[0].counter_volume

    def _delta(self):
        """Compute delta reading.

        Delta meters are just changes in value since last point.
        Sum the the values.
        """
        self.value = 0
        for sample in self._during_samples:
            self.value += sample.counter_volume

    def _calculate(self):
        """Performs the aggregation according to meter type."""
        # Return quick if no samples
        if not self._during_samples:
            self.value = None
            return

        meter_type = self.meter_type
        if meter_type not in ALLOWED_METER_TYPES:
            raise UnknownCounterTypeError(meter_type)

        if meter_type == 'gauge':
            self._gauge()
        elif meter_type == 'cumulative':
            self._cumulative()
        elif meter_type == 'delta':
            self._delta()

    def _set_metadata(self):
        """Pulls metadata from the sample list.

        Metadata is tricky. Some projects like, cinder, treat the resource
        metadata as deleted when the resource is deleted. If we want to
        represent billing/usage information we need to go an extra couple
        of steps to make that metadata available.

        This function will step backward from the end of the sample list
        looking for the last non deleted status sample.
        """
        delete_status = ['deleting', 'deleted']
        status_keys = ['state', 'status']
        samples = self._during_samples

        # If no samples, return early
        if not samples:
            self.metadata = None
            return

        metadata = None
        # Check if sample even has status keys going by last sample.
        has_keys = [
            key in samples[-1].resource_metadata
            for key in status_keys
        ]

        # If sample has keys, loop back from the end.
        if any(has_keys):
            start = max(len(samples) - 1, 0)
            stop = -1
            step = -1
            for i in xrange(start, stop, step):
                # Loop over status fields
                for key in status_keys:
                    status = samples[i].resource_metadata.get(key)
                    if status is not None and status not in delete_status:
                        metadata = samples[i].resource_metadata
                        break
                # Check to see if we found some metadata.
                if metadata is not None:
                    break

        # Default to last sample metadata.
        if metadata is None:
            metadata = samples[-1].resource_metadata
        self.metadata = metadata

    def convert(self, conversion):
        """Convert value using function func.

        :param conversion: Conversion function name
        :type conversion: String|None
        """
        if self.value is None or conversion is None:
            return
        self.value = convert(conversion, self.value)
