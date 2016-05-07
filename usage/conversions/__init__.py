from usage.exc import UnknownConversionError
from pkg_resources import iter_entry_points
from usage.log import logging


logger = logging.getLogger('conversions')

CONVERSIONS = {}
for entry_point in iter_entry_points(group='usage.conversions'):
    try:
        CONVERSIONS[entry_point.name] = entry_point.load()
    except:
        logger.warn('Unable to load conversion {}'.format(entry_point.name))


def convert(name, value):
    """Converts value with conversion name.

    :param name: Name of the conversion, like seconds_to_hours
    :type name: String
    :param value: Value to convert
    :type value: object
    :returns: Converted value
    :rtype: object:
    """
    if name not in CONVERSIONS:
        raise UnknownConversionError(name)

    try:
        new_value = CONVERSIONS[name](value)
    except:
        logger.exception('Unable to convert value \'{}\' with \'{}\''
                         .format(value, name))
        new_value = None
    return new_value
