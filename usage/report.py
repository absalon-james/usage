import config
import csv
import time
import utils
import yaml

from clients import ClientManager
from contextlib import contextmanager
from exc import UnknownLineItemFunction
from log import logging
from meter import Meter


logger = logging.getLogger('usage.report')


class Report:
    line_item_funcs = set([
        'resource_id',
        'timeinterval',
        'invoice_id',
        'billing_entity',
        'payer_account_id',
        'billing_period_start_date',
        'billing_period_end_date',
        'usage_account_id',
        'line_item_type',
        'usage_start_date',
        'usage_end_date',
        'product_code',
        'usage_type',
        'operation',
        'availability_zone',
        'usage_amount',
        'currency_code',
        'item_rate',
        'description',
        'product_name',
        'usage_type'
    ])

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
            self._definition = yaml.load(f)

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

    def metadata_field(self, key, sample):
        """Get value of metadata field is present.

        :param key: Metadata key
        :type key: String
        :param sample: Sample
        :type sample: Sample
        :return: Value of metadata key
        :rtype: String
        """
        value = ''

        # Try nova first nova metadata fields are metadata.<key>
        _, key = key.split(':', 1)
        value = sample.resource_metadata.get('metadata.{}'.format(key), '')
        return value

    def resource_id(self, item, sample, value):
        """Field function to get resource id from a sample

        :param item: Unused
        :type item: Dict
        :param sample: sample
        :type sample: sample
        :param value: Unused
        :type value: Numeric
        :return: Resource id
        :rtype: String
        """
        return sample.resource_id

    def timeinterval(self, item, sample, value):
        """Field function to get report time interval.

        :param item: Item from report definition - Unused
        :type item: Dict
        :param sample: Unused
        :type sample: sample
        :param value: Unused
        :type value: Numeric
        :return: Isoformatted date range
        :rtype: String
        """
        return '/'.join([self._start.isoformat(), self._stop.isoformat()])

    def invoice_id(self, item, sample, value):
        """Get the invoice id.

        TODO - figure out if this is needed.

        :param item: Item from report definition
        :type item: Dict
        :param sample: Unused
        :type sample:Sample
        :param value: Unused
        :type value: Numeric
        :return: invoice_id
        :rtype: String
        """
        return ''

    def billing_entity(self, item, sample, value):
        """Get billing entity.

        Try first from item, then from definition.

        :param item: Item from report definition
        :type item: Dict
        :param sample: Unused
        :type sample:Sample
        :param value: Unused
        :type value: Numeric
        :return: billing_entity
        :rtype: String
        """
        return item.get(
            'billing_entity',
            self._definition.get('billing_entity', ''))

    def payer_account_id(self, item, sample, value):
        """Get payer account id

        # Using the tenant id for now

        :param item: Unused
        :type item: Dict
        :param sample: Sample
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: payer_account_id
        :rtype: String
        """
        return sample.project_id

    def billing_period_start_date(self, item, sample, value):
        """Get billing period start date

        Using the start of the report

        :param item: Unused
        :type item: Dict
        :param sample: Unused
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: isoformatted start date
        :rtype: String
        """
        return self._start.isoformat()

    def billing_period_end_date(self, item, sample, value):
        """Get billing period start date

        Using the stop of the report

        :param item: Unused
        :type item: Dict
        :param sample: Unused
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: isoformatted stop date
        :rtype: String
        """
        return self._stop.isoformat()

    def usage_account_id(self, item, sample, value):
        """Get payer account id

        # Using the project id for now

        :param item: Unused
        :type item: Dict
        :param sample: Sample
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: usage_account_id
        :rtype: String
        """
        return sample.project_id

    def line_item_type(self, item, sample, value):
        """Get line item type.

        Using usage for now. Amazon billing offers usage|tax

        :param item: Item
        :type item: Dict
        :param sample: Sample
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: payer_account_id
        :rtype: String
        """
        return item.get('line_item_type', '')

    def usage_start_date(self, item, sample, value):
        """Get usage start date.

        Should be the max of created_at or the report start.

        :param item: Unused
        :type item: Dict
        :param sample: Sample
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: isoformatted usage_start_date
        :rtype: String
        """
        created_at = sample.resource_metadata.get('created_at')
        if created_at:
            created_at = utils.normalize_time(
                utils.parse_datetime(created_at)
            )
        return max(self._start, created_at).isoformat()

    def usage_end_date(self, item, sample, value):
        """Get usage end date.

        Should be the min of deleted_at or the report stop.

        :param item: Unused
        :type item: Dict
        :param sample: Sample
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: isoformatted usage_start_date
        :rtype: String
        """
        deleted_at = sample.resource_metadata.get('deleted_at')
        if deleted_at:
            deleted_at = utils.normalize_time(
                utils.parse_datetime(deleted_at)
            )
            ret = min(self._stop, deleted_at)
        else:
            ret = self._stop
        return ret.isoformat()

    def product_code(self, item, sample, value):
        """Get product code

        :param item: Item containing product code.
        :type item: Dict
        :param sample: Sample
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: product code from item
        :rtype: String
        """
        return item.get('product_code', '')

    def usage_type(self, item, sample, value):
        """Get usage type from item

        :param item: Item containing product code.
        :type item: Dict
        :param sample: Sample
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: usage_type
        :rtype: String
        """
        return item.get('usage_type', '')

    def operation(self, item, sample, value):
        """Get operation from item.

        :param item: Item containing product code.
        :type item: Dict
        :param sample: Sample
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: operation
        :rtype: String
        """
        return item.get('operation')

    def availability_zone(self, item, sample, value):
        """Get availability zone froms sample metadata

        :param item: Unused
        :type item: Dict
        :param sample: Sample
        :type sample: Sample
        :param value: Unused
        :type value: Numeric
        :return: availability zone
        :rtype: String
        """
        return sample.resource_metadata.get('availability_zone', '')

    def usage_amount(self, item, sample, value):
        """Get meter value

        :param item: Unused
        :type item: Dict
        :param sample: Unused
        :type sample: Sample
        :param value: Meter value
        :type value: Numeric
        :return: isoformatted usage_start_date
        :rtype: String
        """
        return value

    def currency_code(self, item, sample, value):
        """Get the currency code.

        Check the item first.
        Check the definition next.

        :param item: Item
        :type item: dict
        :param sample: Unused
        :type sample: sample
        :param value: Unused
        :type value: Numeric
        :return: Currency code
        :rtype: String
        """
        return item.get(
            'currency_code',
            self._definition.get('currency_code', '')
        )

    def item_rate(self, item, sample, value):
        """Get the item rate from the item.

        :param item: item with the item rate
        :type item: dict
        :param sample: Unused
        :type sample: sample
        :param value: Unused
        :type value: numeric
        :return: Item rate
        :rtype: Float
        """
        return item.get('item_rate', 0.0)

    def description(self, item, sample, value):
        """Get the description from the item.

        :param item: item with description. Default to ''.
        :type item: dict
        :param sample: Unused
        :type sample: sample
        :param value: Unused
        :type value: Numeric
        :return: Description from item
        :rtype: String
        """
        return item.get('description', '')

    def product_name(self, item, sample, value):
        """Get the product name from the item.

        Defaults to ''.

        :param item: Item with product_name
        :type item: dict
        :param sample: Unused
        :type sample: sample
        :param value: Unused
        :type value: Numeric
        :return: Product name
        :rtype: String
        """
        return item.get('product_name', '')

    def _field_function(self, func, item, sample, value):
        """Call a field function.

        :param func: Name of the field function.
        :type func: String
        :param item: Item - passed to the field function
        :type item: dict
        :param sample: Sample - passed to the field function
        :type sample: sample
        :param value: Value|Volume|Amount of the item.
                      Passed to the field function.
        :type value: Numeric
        :return: Result of the field function.
        :rtype: String|Numeric
        """
        # Transform function name into a python compatible function name.
        # TODO - Move towards more sophisticated function mapping.
        func = func.lower().replace(' ', '_').replace('.', '_')

        # Func of the form metadata:<some key> is a special case
        if func not in self.line_item_funcs:
            if func.startswith('metadata:'):
                return self.metadata_field(func, sample)
            raise UnknownLineItemFunction(func)
        return getattr(self, func)(item, sample, value)

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
                self._definition.get('fieldnames')
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
        fieldnames = self._definition.get('fieldnames', [])
        items = self._definition.get('items', [])

        with self.csv_scope() as csv_scope:
            # Iterate over items in definition.
            for item in items:
                m = Meter(self._client, item['meter_name'])
                # Meter.read() returns a generator that
                # yields a (sample, value) tuple.
                # The sample contains resource metadata.
                for sample, value in m.read(start=self._start,
                                            stop=self._stop):
                    line_item = {
                        f: self._field_function(f, item, sample, value)
                        for f in fieldnames
                    }
                    csv_scope.writerow(line_item)

        elapsed = time.time() - report_start
        logger.info('Report is at {}'.format(self.csv_filename))
        logger.debug('Finished report in {} seconds'.format(elapsed))


if __name__ == '__main__':
    conf = config.load('/etc/usage/usage.yaml')
    manager = ClientManager(**conf.get('auth_kwargs', {}))
    ceilometer = manager.get_ceilometer()
    r = Report(ceilometer, '/etc/usage/report.yaml')
    r.run()
