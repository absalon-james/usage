def bytes_to_gigabytes(b):
    """Convert B to GB.

    :param b: A size in bytes
    :type b: Float
    :return: Size in GB
    :rtype: Float
    """
    return b / 1024 / 1024 / 1024
