from usage.exc import UnknownFieldFunctionError
from pkg_resources import iter_entry_points
from usage.log import logging


logger = logging.getLogger('fields')

FIELD_FUNCTIONS = {}
for entry_point in iter_entry_points(group='usage.fields'):
    try:
        FIELD_FUNCTIONS[entry_point.name] = entry_point.load()
    except:
        logger.warn(
            'Unable to load field function {}'.format(entry_point.name))


def field_function(name, definition, item, reading):
    """Run a field function. Always send defintion, item, and reading.

    :param name: Name of the field function
    :type name: String
    :param definition: Report definition
    :type definition: dict
    :param item: Item in report definition. Describes how to make a row.
    :type item: dict
    :param reading: Meter reading for the item.
    :type reading: usage.reading.Reading
    :returns: Field function result
    :rtype: object:
    """
    if name not in FIELD_FUNCTIONS:
        raise UnknownFieldFunctionError(name)

    try:
        value = FIELD_FUNCTIONS[name](definition, item, reading)
    except:
        logger.exception('Unable to get value for field function {}'
                         .format(name))
        value = None
    return value
