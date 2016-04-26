class InvalidTimeRangeError(Exception):
    """Error for invalid time ranges."""
    def __init__(self, start, stop):
        msg = 'Start time {} exceeds stop time {}'.format(
            start.isoformat(),
            stop.isoformat()
        )
        super(InvalidTimeRangeError, self).__init__(msg)


class UnknownCounterTypeError(Exception):
    """Error for unknown counter types."""
    def __init__(self, counter_type):
        msg = 'Encountered unknown counter type {}'.format(counter_type)
        super(UnknownCounterTypeError, self).__init__(msg)
