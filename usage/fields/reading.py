import ast

from usage.log import logging

_ALLOWED_RESOURCE_ATTRS = ['resource_id', 'project_id', 'metadata']

logger = logging.getLogger('usage.fields')


def _get_reading_attr(reading, attr):
    """Get an attribute of a reading.

    :param reading: Meter reading.
    :type reading: usage.reading.Reading
    :param attr: Name of the attr
    :type attr: String
    :returns: Attribute if an allowed attribute or None
    :rtype: Object|None
    """
    if attr in _ALLOWED_RESOURCE_ATTRS:
        return getattr(reading, attr)
    return None


def metadata_field(key, r):
    """Get value of metadata field if present.

    Special field function that is not called like the others.
    Only accepts a key parameter and a reading.

    :param key: Metadata key. Looks like metadata:<real key>
    :type key: String
    :param reading: Meter reading.
    :type reading: usage.reading.Reading
    :return: Value of metadata key
    :rtype: String
    """
    value = None

    # Parse the actual key
    _, key = key.split(':', 1)

    metadata = _get_reading_attr(r, 'metadata')

    # Try nova first nova metadata fields are metadata.<key>
    value = metadata.get('metadata.{}'.format(key))

    # Try glance next. Glance metadata fields are properties.<key>
    if not value:
        value = metadata.get('properties.{}'.format(key))

    # Try cinder next.
    # Metadata fields are stored as a list of metadata objects.
    if not value:
        cinder_data = metadata.get('metadata')
        if isinstance(cinder_data, unicode) or isinstance(cinder_data, str):
            try:
                cinder_data = ast.literal_eval(cinder_data)
                for obj in cinder_data:
                    if obj.get('key') == key:
                        value = obj.get('value')
                        break
            except Exception:
                pass

    return value


def availability_zone(d, i, r):
    """Get availability zone from reading metadata.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: availability zone
    :rtype: String
    """
    return r.metadata.get('availability_zone', '')


def billing_period_end_date(d, i, r):
    """Get billing period start date

    Using the stop of the report

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: isoformatted stop date
    :rtype: String
    """
    return r.stop.isoformat()


def billing_period_start_date(d, i, r):
    """Get billing period start date

     Using the start of the reading.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: isoformatted start date
    :rtype: String
    """
    return r.start.isoformat()


def display_name(d, i, r):
    """Get the resource display name.

    :param d: Report definition.
    :type d: Dict
    :param i: Item definition.
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    """
    return r.metadata.get('display_name')


def instance_type(d, i, r):
    """get instance type.

    :param d: Report definition.
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    """
    return r.metadata.get('instance_type')


def payer_account_id(d, i, r):
    """Get payer account id

    Using the project id for now.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: payer_account_id
    :rtype: String
    """
    return _get_reading_attr(r, 'project_id')


def resource_id(d, i, r):
    """Get resource id from meter reading.

    :param d: Report definition
    :type: d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    """
    return _get_reading_attr(r, 'resource_id')


def timeinterval(d, i, r):
    """Get isoformatted time interval from reading.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: Isoformatted date range
    :rtype: String
    """
    return '/'.join([r.start.isoformat(), r.stop.isoformat()])


def usage_account_id(d, i, r):
    """Get payer account id from reading.

    Using the project id for now

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: reading.project_id
    :rtype: String
    """
    return r.project_id


def usage_amount(d, i, r):
    """Get meter value

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: isoformatted usage_start_date
    :rtype: String
    """
    return r.value


def usage_end_date(d, i, r):
    """Get usage end date from reading.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: isoformatted usage_start_date
    :rtype: String
    """
    return r.usage_stop.isoformat()


def usage_start_date(d, i, r):
    """Get usage start date from reading.

    :param d: Report definition
    :type d: Dict
    :param i: Item definition
    :type i: Dict
    :param r: Meter reading
    :type r: usage.reading.Reading
    :return: isoformatted usage_start_date
    :rtype: String
    """
    return r.usage_start.isoformat()
