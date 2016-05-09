def billing_entity(d, i, r):
    """Get billing entity.

    Try first from item, then from definition.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading.
    :type r: usage.reading.Reading
    :return: billing_entity
    :rtype: String
    """
    return i.get('billing_entity', d.get('billing_entity', ''))


def currency_code(d, i, r):
    """Get currency code.

    Try first from item, then from definition.

    :param d: Report definition.
    :type d: Dict
    :param i: Item definition
    :type d: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :returns: currency code
    :rtype: String
    """
    return i.get('currency_code', d.get('currency_code', ''))


def description(d, i, r):
    """Get the description from the item.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: Description from item
    :rtype: String
    """
    return i.get('description', '')


def item_rate(d, i, r):
    """Get the item rate from the item.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: Item rate. Defaults to 0.0
    :rtype: Float
    """
    return i.get('item_rate', 0.0)


def line_item_type(d, i, r):
    """Get line item type from item.

    Using usage for now. Amazon billing offers usage|tax

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: payer_account_id
    :rtype: String
    """
    return i.get('line_item_type', '')


def meter_name(d, i, r):
    """Get meter name from item.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading.
    :type r: usage.reading.Reading
    :return: Name of the meter
    :rtype: String
    """
    return i.get('meter_name')


def operation(d, i, r):
    """Get operation from item.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: operation
    :rtype: String
    """
    return i.get('operation', '')


def product_code(d, i, r):
    """Get product code

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: product code from item
    :rtype: String
    """
    return i.get('product_code', '')


def product_name(d, i, r):
    """Get the product name from the item.

    Defaults to ''.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: Product name
    :rtype: String
    """
    return i.get('product_name', '')


def usage_type(d, i, r):
    """Get usage type from item

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: usage_type
    :rtype: String
    """
    return i.get('usage_type', '')
