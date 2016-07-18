import csv
import yaml

from pkg_resources import iter_entry_points
from usage.log import logging

logger = logging.getLogger('usage.licensing')

_LICENSERS = {}
for entry_point in iter_entry_points(group='usage.licensers'):
    try:
        _LICENSERS[entry_point.name] = entry_point.load()
    except:
        logger.exception(
            'Unable to load licenser {}'.format(entry_point.name))


class Licensing:
    """
    This class will create licensing summaries according to a definition.
    """
    def __init__(self,
                 domain_client=None,
                 input_file=None,
                 definition_file=None):
        """Inits the licensing object.

        :param domain_client: Domain client instance.
        :type domain_client: usage.clients.DomainClient
        :param input_file: Name of the input file.
        :type input_file: String
        :param definition_file: Name of the definition file
        :type definition_file: String
        """
        self._domain_client = domain_client
        self._input_file = input_file
        self._definition_file = definition_file

        self._load_definition()
        self._read()

    def _load_definition(self):
        """Load the licensing definition."""
        with open(self._definition_file) as f:
            self._definition = yaml.safe_load(f)

        self._licensers = []
        for l_dict in self._definition.get('licensers'):
            t = l_dict.pop('type')
            self._licensers.append(_LICENSERS[t](**l_dict))

    def _handle_row(self, row):
        """Handles a single csv row.

        Pass the row to each licenser in the definition.

        :param row: Csv row to handle
        :type row: dict
        """
        for licenser in self._licensers:
            licenser.handle_row(row)

    def _read(self):
        """Read the csv input file."""
        with open(self._input_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self._handle_row(row)

    def output(self):
        """Print out results."""
        print ''
        for l in self._licensers:
            l.output()
            print ''
        print ''
