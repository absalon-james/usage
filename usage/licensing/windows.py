from common import CountLicenser as BaseCountLicenser
from common import HourLicenser as BaseHourLicenser
from common import INDENTSIZE
from common import MAXLINESIZE
from usage.log import logging

logger = logging.getLogger('usage.licensing.windows')

_DISTRO_KEY = 'image:OS Distro'
_VERSION_KEY = 'image:OS Version'
_GROUPBY = [
    'domain',
    _DISTRO_KEY,
    _VERSION_KEY
]
_RELEVANT_OSES = [
    'windows'
]


def _relevant(row):
    """Determine if row is relevant to windows licensers.

    :param row: Row
    :type row: Dict
    :returns: True if row is relevant.
    :rtype: Bool
    """
    if row.get(_DISTRO_KEY).lower() in _RELEVANT_OSES:
        if row.get(_VERSION_KEY):
            return True
    return False


def _row_cost(row, costs, quantity):
    """Determine cose of the row.

    :param row: Row
    :type row: Dict
    :param costs: Dictionary of costs keyed by distro, then by version
    :type costs: Dict
    :param quantity: Numeric amount the row represents.
        To be multiplied by a rate.
    :type quantity: Int|Float
    :returns: Quantity multiplied by cost per unit of quantity
    :rtype: Float
    """
    distro = row.get(_DISTRO_KEY)
    version = row.get(_VERSION_KEY)
    cost = 0.0
    try:
        rate = costs[row.get(_DISTRO_KEY)][row.get(_VERSION_KEY)]
        cost = float(rate) * quantity
    except KeyError:
        logger.exception(
            'Unable to find rate for {} version:{}'
            .format(distro, version)
        )
    return cost


class CountLicenser(BaseCountLicenser):
    """Licenser that counts instances of windows distros by version."""
    def __init__(self,
                 project_id_field=None,
                 costs=None):
        """Inits the licenser

        :param project_id_field: Name of the field containing the project id
        :type project_id_field: String
        :param costs: Dictionary containing
            rates per instance of distro-version pair.
        :type costs: Dict
        """
        if costs is None:
            costs = {}
        self._costs = costs
        self._title = 'Windows Licensing Count'
        super(CountLicenser, self).__init__(
            groupby=_GROUPBY,
            project_id_field=project_id_field
        )

    def _relevant(self, row):
        """Determine if row is relevant to the licenser.

        :param row: Row
        :type row: Dict
        :returns: True if relevant
        :rtype: Boolean
        """
        return _relevant(row)

    def _row_cost(self, row):
        """Determine the cost of the row.

        :param row: Csv row
        :type row: Dict
        :returns: Cost of the row
        :rtype: Float
        """
        return _row_cost(row, self._costs, 1)

    def _format_leaf(self, name, node, indents):
        """Formats a leaf row of output.

        A leaf row is a node in data without any children
        without any groups below it.

        :param name: Name of the leaf
        :type name: String
        :param node: Node in the data. Should have count.
        :type node: Dict
        :param indents: Number of indents so far.
        :type indents: Int
        :returns: Formatted lead node string
        :rtype: Str
        """
        indent = ' ' * indents * INDENTSIZE
        count = '{:5d} count = '.format(node['count'])
        number = '{:10.2f}'.format(node['cost'])
        formatstr = '{}{:<%d}{}{}' % (
            MAXLINESIZE - len(indent) - len(number) - len(count)
        )
        return formatstr.format(indent, name, count, number)


class HourLicenser(BaseHourLicenser):
    """Licenser that counts hours of windows usage."""
    def __init__(self,
                 project_id_field=None,
                 hours_field=None,
                 costs=None):
        """Inits the licenser.

        :param project_id_field: Name of the field in the report
            containing the project id for a resource.
        :type project_id_field: String
        :param hours_field: Name of the field in the report
            containing the hours field for a resource.
        :type hours_field: String
        :param costs: Dictionary that contains costs per hour of
            usage keyed by distro and then version.
        :type costs: Dict
        """
        if costs is None:
            costs = {}
        self._costs = costs
        self._title = 'Windows Licensing by the hour'
        super(HourLicenser, self).__init__(
            groupby=_GROUPBY,
            project_id_field=project_id_field,
            hours_field=hours_field
        )

    def _relevant(self, row):
        """Determine if row is relevant to the licenser.

        :param row: Row
        :type row: Dict
        :returns: True if relevant
        :rtype: Boolean
        """
        return _relevant(row)

    def _row_cost(self, row):
        """Determine the cost of the row.

        :param row: Csv row
        :type row: Dict
        :returns: Cost of the row
        :rtype: Float
        """
        quantity = float(row.get(self._hours_field))
        return _row_cost(row, self._costs, quantity)

    def _format_leaf(self, name, node, indents):
        """Formats a leaf row of output.

        A leaf row is a node in data without any children
        without any groups below it.

        :param name: Name of the leaf
        :type name: String
        :param node: Node in the data. Should have count.
        :type node: Dict
        :param indents: Number of indents so far.
        :type indents: Int
        :returns: Formatted lead node string
        :rtype: Str
        """
        indent = ' ' * indents * INDENTSIZE
        hours = '{:5.2f} hours = '.format(node['hours'])
        number = '{:10.2f}'.format(node['cost'])
        formatstr = '{}{:<%d}{}{}' % (
            MAXLINESIZE - len(indent) - len(number) - len(hours)
        )
        return formatstr.format(indent, name, hours, number)
