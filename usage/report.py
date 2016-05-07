import csv
import time
import utils
import yaml

from contextlib import contextmanager
from exc import UnknownFieldFunctionError
from fields import field_function
from fields.reading import metadata_field
from log import logging
from meter import Meter


logger = logging.getLogger('usage.report')


class Report:
    """Report class."""
    def __init__(self,
                 client,
                 definition_filename,
                 csv_filename,
                 start=None,
                 stop=None):
        """Read in report definition from file.

        :param definition_filename: Name of report definition file.
        :type definition_filename: String
        :param csv_filename: Name of the output file without dates.
        :type csv_filename: String
        :param start: Start of report in utc
        :type start: Datetime
        :param stop: Stop of report in utc
        :type stop: Datetime
        """
        self._definition_filename = definition_filename
        self._definition = None
        self._load_definition()

        self._csv_filename = csv_filename
        self._headers_written = False

        self._client = client

        default_start, default_stop = utils.mtd_range()
        self._start = start or default_start
        self._stop = stop or default_stop

    def _load_definition(self):
        """Load a report definition."""
        with open(self._definition_filename, 'r') as f:
            self._definition = yaml.safe_load(f)

    @property
    def csv_filename(self):
        """Create a csv filename.

        The date range will be added.

        :return: CSV output filename
        :rtype: String
        """
        csv_filename = self._csv_filename
        if csv_filename.endswith('.csv'):
            csv_filename, _ = csv_filename.rsplit('.')
        return '{}_{}_to_{}.csv'.format(
            csv_filename,
            self._start.isoformat(),
            self._stop.isoformat()
        )

    def _field_function(self, func, item, reading):
        """Call a field function.

        :param func: Name of the field function.
        :type func: String
        :param item: Item in report definition
        :type item: Dict
        :param reading: Resource meter reading
        :type reading: reading.Reading
        :return: Result of the field function.
        :rtype: String|Numeric|None
        """
        # Transform function name into a python compatible function name.
        # TODO - Move towards more sophisticated function mapping.
        func = func.lower().replace(' ', '_').replace('.', '_')
        try:
            return field_function(func, self._definition, item, reading)
        except UnknownFieldFunctionError as uffe:
            if func.startswith('metadata:'):
                return metadata_field(func, reading)
            raise uffe

    @contextmanager
    def csv_scope(self):
        """Get a csv writer context.

        :yield: csv.DictWriter
        """
        filename = self.csv_filename
        csv_file = None
        try:
            # Open in append mode
            csv_file = open(filename, 'a')
            writer = csv.DictWriter(
                csv_file,
                [c['name'] for c in self._definition.get('columns')]
            )
            # Write csv column headers
            if not self._headers_written:
                writer.writeheader()

            yield writer
        finally:
            if csv_file:
                csv_file.close()

    def run(self):
        """Run the report."""
        report_start = time.time()
        columns = self._definition.get('columns', [])
        items = self._definition.get('items', [])

        with self.csv_scope() as csv_scope:
            # Iterate over items in definition.
            for item in items:
                m = Meter(self._client, item['meter_name'])
                # Meter.read() returns a generator that yields readings.
                # One reading per resource/meter pair
                for reading in m.read(start=self._start, stop=self._stop):
                    reading.convert(item.get('conversion'))
                    line_item = {
                        c.get('name'):
                            self._field_function(c.get('func'), item, reading)
                        for c in columns
                    }
                    csv_scope.writerow(line_item)

        elapsed = time.time() - report_start
        logger.info('Report is at {}'.format(self.csv_filename))
        logger.debug('Finished report in {} seconds'.format(elapsed))
