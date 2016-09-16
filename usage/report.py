import csv
import time
import utils
import yaml

from contextlib import contextmanager
from exc import UnknownFieldFunctionError
from fields import field_function
from fields.reading import image_metadata_field
from fields.reading import metadata_field
from log import logging
from meter import Meter


logger = logging.getLogger('usage.report')


class Report:
    """Report class."""
    def __init__(self,
                 client,
                 definition_filename,
                 output,
                 max_samples=15000,
                 start=None,
                 stop=None):
        """Read in report definition from file.

        :param client: Ceilometer client
        :type client:
        :param definition_filename: Name of report definition file.
        :type definition_filename: String
        :param output: Output object with stream attribute
        :type output: output.File|output.Stream
        :param max_samples: Number of samples per query max.
        :type max_samples: Integer
        :param start: Start of report in utc
        :type start: Datetime
        :param stop: Stop of report in utc
        :type stop: Datetime
        """
        self._definition_filename = definition_filename
        self._definition = None
        self._load_definition()

        self.output = output
        self._headers_written = False
        self.max_samples = max_samples

        self._client = client

        default_start, default_stop = utils.mtd_range()
        self._start = start or default_start
        self._stop = stop or default_stop

    def _load_definition(self):
        """Load a report definition."""
        with open(self._definition_filename, 'r') as f:
            self._definition = yaml.safe_load(f)

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
            elif func.startswith('image_metadata:'):
                return image_metadata_field(func, reading)
            raise uffe

    @contextmanager
    def csv_scope(self):
        """Get a csv writer context.

        :yield: csv.DictWriter
        """
        # Open in append mode
        writer = csv.DictWriter(
            self.output.stream,
            [c['name'] for c in self._definition.get('columns')]
        )
        # Write csv column headers
        if not self._headers_written:
            writer.writeheader()
        yield writer

    def run(self):
        """Run the report."""
        report_start = time.time()
        columns = self._definition.get('columns', [])
        items = self._definition.get('items', [])

        with self.csv_scope() as csv_scope:
            # Iterate over items in definition.
            for item in items:
                m = Meter(
                    self._client,
                    item['meter_name'],
                    max_samples=self.max_samples
                )
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
        logger.info('Report is at {}'.format(self.output.location))
        logger.debug('Finished report in {} seconds'.format(elapsed))
