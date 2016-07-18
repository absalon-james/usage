from common import CountLicenser as BaseCountLicenser
from common import HourLicenser as BaseHourLicenser
from common import INDENTSIZE
from common import MAXLINESIZE
from usage.log import logging

logger = logging.getLogger('usage.licensing.sqlserver')

_EDITION_KEY = 'image:SQLServer Edition'
_VERSION_KEY = 'image:SQLServer Version'
_GROUPBY = [
    'domain',
    _EDITION_KEY,
    _VERSION_KEY
]


def _relevant(row):
    """Determine if row is relevant to SqlServer licensers.

    :param row: Row
    :type row: Dict
    :returns: True if row is relevant.
    :rtype: Bool
    """
    if row.get(_EDITION_KEY):
        if row.get(_VERSION_KEY):
            return True
    return False


def _row_cost(row, costs, quantity):
    """Determine cose of the row.

    :param row: Row
    :type row: Dict
    :param costs: Dictionary of costs keyed by edition, then by version
    :type costs: Dict
    :param quantity: Numeric amount the row represents.
        To be multiplied by a rate.
    :type quantity: Int|Float
    :returns: Quantity multiplied by cost per unit of quantity
    :rtype: Float
    """
    edition = row.get(_EDITION_KEY)
    version = row.get(_VERSION_KEY)
    cost = 0.0
    try:
        rate = costs[row.get(_EDITION_KEY)][row.get(_VERSION_KEY)]
        cost = float(rate) * quantity
    except KeyError:
        logger.exception(
            'Unable to find rate for SQLServer Edition: {} Version:{}'
            .format(edition, version)
        )
    return cost


class CountLicenser(BaseCountLicenser):
    """
    Licenser that counts instances of sqlserver usage by edition and version.
    """
    def __init__(self,
                 project_id_field=None,
                 costs=None):
        """Init the licenser

        :param project_id_field: Name of the field containing the project id
        :type project_id_field: String
        :param costs: Dictionary containing
            rates per instance of edition-version pair.
        :type costs: Dict
        """
        if costs is None:
            costs = {}
        self._costs = costs
        self._title = 'SQLServer Licensing Count'
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
    """Licenser that counts hours of sqlserver usage."""
    def __init__(self,
                 project_id_field=None,
                 hours_field=None,
                 costs=None):
        """Inits the licenser

        :param project_id_field: Name of the field containing the project id
        :type project_id_field: String
        :param costs: Dictionary containing
            rates per instance of edition-version pair.
        :type costs: Dict
        """
        if costs is None:
            costs = {}
        self._costs = costs
        self._title = 'SQLServer Licensing by the hour'
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
