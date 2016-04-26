def query(field, op, value, type=''):
    """Assemble a dict representing a query filter.

    :param field: Field to query
    :type field: String
    :param op: Query operator
    :type op: String
    :param value: Value to query
    :type value: String
    :param type: Type of the value
    :type type: String
    :return: Query filter dict
    :rtype: Dict
    """
    return {
        'field': field,
        'op': op,
        'value': value,
        'type': type
    }
