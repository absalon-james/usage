from usage.domain_cache import get_domain_name
from usage.log import logging


logger = logging.getLogger('usage.licensing.common')

INDENTSIZE = 4
MAXLINESIZE = 79

FILL = {0: ' ', 1: ' '}


class Licenser(object):
    """Base licenser class with common functionality."""
    def __init__(self, project_id_field='Project Id', groupby=None):
        """Inits the licenser

        :param project_id_field: Name of the field in a csv report
            containing the project id of a resource.
        :type project_id_field: Str
        :param groupby: List of fields in a report to group results by.
        :type groupby: List
        """
        self._project_id_field = project_id_field
        if groupby is None:
            groupby = ['domain']
        self._groupby = groupby
        self._data = {}

    def _relevant(self, row):
        """Determine if row is relevant to licenser.

        The base functionality is to always return True.
        Subclasses should implement their own version of this method.

        :param row: Row
        :type row: Dict
        :returns: True or False
        :rtype: Boolean
        """
        return True

    def _row_cost(self, row):
        """Determine the cost of the row.

        The base functionality is to always return 0.0.
        Subclasses should implement this method.

        :param row: Row
        :type row: Dict
        :returns: Cost of the row
        :rtype: Float
        """
        return 0.0

    def _drill_down(self, row):
        """Drill down into the data based on groupby.

        :param row: Row
        :type row: Dict
        :returns: Node in dictionary at bottom of groupby
        :rtype: Dict
        """
        current = self._data
        for field in self._groupby:
            if field == 'domain':
                key = get_domain_name(row.get(self._project_id_field))
            else:
                key = row.get(field) or 'unknown'
            current = current.setdefault(key, {})
        return current

    def _dft_total(self, node):
        """Sums totals using recursive depth first traversal.

        :param node: Node in data
        :type node: Dict
        :returns: Total of children
        :rtype: float
        """
        # Base cases
        if not isinstance(node, dict):
            return node

        if 'cost' in node:
            return node['cost']

        total = 0.0
        for key, value in node.iteritems():
            if key == 'total':
                continue
            total += self._dft_total(value)
        node['total'] = total
        return total

    def _format_node(self, name, node, indents):
        """Format an output row for a node in data with children.

        :param name: Name of the node
        :type name: Str
        :param node: Node
        :type node: Dict
        :param indents: Number of indents
        :type indents: Int
        :returns: The formatted string.
        :rtype: Str
        """
        indent = ' ' * indents * INDENTSIZE
        number = '{:10.2f}'.format(node['total'])
        formatstr = '{}{:%s<%d}{}' % (
            FILL.get(indents % 2),
            MAXLINESIZE - len(indent) - len(number)
        )
        return formatstr.format(indent, name, number)

    def _format_leaf(self, name, node, indents):
        """Format an output row for a node in data without children.

        :param name: Name of the node
        :type name: Str
        :param node: Node in data
        :type node: Dict
        :param indents: Number of indents
        :type indents: Int
        """
        indent = ' ' * indents * INDENTSIZE
        number = '{:10.2f}'.format(node['cost'])
        formatstr = '{}{:%s<%d}{}' % (
            FILL.get(indents % 2),
            MAXLINESIZE - len(indent) - len(number)
        )
        return formatstr.format(indent, name, number)

    def _output_node(self, name, node, indents=0):
        """Print the string representation of the node.

        :param name: Name of the node.
        :type name: Str
        :param node: Node in data
        :type node: Dict
        :param indents: Number of indents.
        :type indents: Int
        """
        # Leaf nodes will have a cost key
        if 'cost' in node:
            print self._format_leaf(name, node, indents)
            return
        print self._format_node(name, node, indents)
        # Iterate over children
        for node_name, node in node.iteritems():
            if node_name != 'total':
                self._output_node(node_name, node, indents + 1)

    def handle_row(self, row):
        """Handle a row.

        The base functionality is to do nothing. Subclasses should implement
        this method.

        :param row: Row to handle
        :type row: Dict
        """
        pass

    def output(self):
        """Print output of the licenser."""
        # Roll up total costs
        self._dft_total(self._data)

        # Optionally print a title
        if hasattr(self, '_title'):
            print self._title
            print '=' * len(self._title)

        # Iterate children
        for node_name, node in self._data.iteritems():
            if node_name != 'total':
                self._output_node(node_name, node, 0)


class HourLicenser(Licenser):
    """Base hour licenser class."""
    def __init__(self,
                 project_id_field=None,
                 hours_field=None,
                 groupby=None):
        """Inits the licenser.

        :param project_id_field: Name of the field in a csv
            report containing the project id for a resource.
        :type project_id_field: Str
        :param hours_field: Name of the field in a csv report
            containing the hours of usage for a resource.
        :type hours_field: Str
        :param groupby: List of fields to group by.
        :type groupby: List
        """
        super(HourLicenser, self).__init__(
            project_id_field=project_id_field,
            groupby=groupby
        )
        self._hours_field = hours_field or 'Hours'

    def handle_row(self, row):
        """Handle a csv row.

        :param row: Row to handle
        :type row: Dict
        """
        # ignore irrelevant rows
        if not self._relevant(row):
            return

        data = self._drill_down(row)

        hours = data.setdefault('hours', 0.0)
        hours += float(row.get(self._hours_field))
        data['hours'] = hours

        cost = data.setdefault('cost', 0.0)
        cost += self._row_cost(row)
        data['cost'] = cost


class CountLicenser(Licenser):
    def handle_row(self, row):
        """Handle a csv row.

        :param row: Row to handle
        :type row: Dict
        """
        if not self._relevant(row):
            return

        data = self._drill_down(row)

        count = data.setdefault('count', 0)
        count += 1
        data['count'] = count

        cost = data.setdefault('cost', 0.0)
        cost += self._row_cost(row)
        data['cost'] = cost
