import datetime
import iso8601


def mtd_range():
    """Get a month to date datetime range.

    :return: (utc beginning of month, utcnow)
    :rtype: tuple
    """
    stop = datetime.datetime.utcnow()
    start = datetime.datetime(stop.year, stop.month, 1)
    return (start, stop)


def today_range():
    """Get a today datetime range.

    :return: (utc beginning of day, utcnow)
    :rtype: tuple
    """
    stop = datetime.datetime.utcnow()
    start = datetime.datetime(stop.year, stop.month, stop.day)
    return (start, stop)


def last_hour_range():
    """Get last hour datetime range.

    :return: (utc one hour ago, utc now)
    :rtype: tuple
    """
    stop = datetime.datetime.utcnow()
    start = stop - datetime.timedelta(seconds=3600)
    return (start, stop)


def parse_datetime(date_str):
    """Parse a datetime object from a string.

    :param date_str: String to parse
    :type date_str: String
    :return: Parse datetime object
    :rtype: datetime.datetime
    """
    return iso8601.parse_date(date_str)


def normalize_time(timestamp):
    """Normalize time in arbitrary timezone to UTC naive object.

    Taken from oslo.utils.timeutils
    """
    offset = timestamp.utcoffset()
    if offset is None:
        return timestamp
    return timestamp.replace(tzinfo=None) - offset
