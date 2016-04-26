def bytes_to_gigabytes(b):
    """Convert B to GB.

    :param b: A size in bytes
    :type b: Float
    :return: Size in GB
    :rtype: Float
    """
    return b / 1024 / 1024 / 1024


def seconds_to_hours(s):
    """Convert seconds to hours:

    :param s: Number of seconds
    :type s: Float
    :return: Number of hours
    :rtype: Float
    """
    return s / 3600
