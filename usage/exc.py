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


class UnknownConversionError(Exception):
    """Error for unknown conversion."""
    def __init__(self, conversion_name):
        msg = 'Unknown conversion {}.'.format(conversion_name)
        super(UnknownConversionError, self).__init__(msg)


class UnknownFieldFunctionError(Exception):
    """Error for unknown field functions."""
    def __init__(self, function_name):
        msg = 'Unknown field function {}.'.format(function_name)
        super(UnknownFieldFunctionError, self).__init__(msg)


class NoSamplesError(Exception):
    """Error for no samples."""
    def __init__(self):
        msg = "Resource does not have any samples during the time period."
        super(NoSamplesError, self).__init__(msg)
