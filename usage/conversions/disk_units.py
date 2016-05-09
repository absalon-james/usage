def bytes_to_gigabytes(b):
    """Convert B to GB.

    :param b: A size in bytes
    :type b: Float
    :return: Size in GB
    :rtype: Float
    """
    return b / 1024 / 1024 / 1024


def megabytes_to_gigabytes(mb):
    """Convert MB to GB.

    :param mb: A size in MegaBytes
    :type mb: Float
    :return: Size in GB
    :rtype: Float
    """
    return mb / 1024
