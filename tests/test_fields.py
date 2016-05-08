import datetime
import mock
import unittest

from fakes import FakeReading
from usage.fields import field_function
from usage.fields.item import billing_entity
from usage.fields.item import currency_code
from usage.fields.item import description
from usage.fields.item import item_rate
from usage.fields.item import line_item_type
from usage.fields.item import operation
from usage.fields.item import product_code
from usage.fields.item import product_name
from usage.fields.item import usage_type
from usage.fields.reading import availability_zone
from usage.fields.reading import billing_period_end_date
from usage.fields.reading import billing_period_start_date
from usage.fields.reading import display_name
from usage.fields.reading import instance_type
from usage.fields.reading import metadata_field
from usage.fields.reading import payer_account_id
from usage.fields.reading import resource_id
from usage.fields.reading import timeinterval
from usage.fields.reading import usage_account_id
from usage.fields.reading import usage_amount
from usage.fields.reading import usage_end_date
from usage.fields.reading import usage_start_date
from usage.fields.report import invoice_id
from usage.exc import UnknownFieldFunctionError


def broken_field(d, i, r):
    raise Exception("I am broken.")
    return 'worked'


class TestFieldFunction(unittest.TestCase):
    """Tests the conversion plugin loaded."""
    def test_unknown_field_function(self):
        with self.assertRaises(UnknownFieldFunctionError):
            field_function('doesntexist', 'd', 'i', 'r')

    @mock.patch(
        'usage.fields.FIELD_FUNCTIONS',
        {'broken_field': broken_field}
    )
    def test_broken_field_function(self):
        self.assertTrue(
            field_function('broken_field', 'd', 'i', 'r') is None
        )


class TestMetadataField(unittest.TestCase):
    """Tests the metadata field function."""

    key = 'metadata:test'

    def test_metadata_field_not_present(self):
        r = FakeReading(metadata={})
        self.assertTrue(metadata_field(self.key, r) is None)

    def test_nova_metadata(self):
        metadata = {'metadata.test': 'nova'}
        r = FakeReading(metadata=metadata)
        self.assertEquals(metadata_field(self.key, r), 'nova')

    def test_glance_metdata(self):
        metadata = {'properties.test': 'glance'}
        r = FakeReading(metadata=metadata)
        self.assertEquals(metadata_field(self.key, r), 'glance')

    def test_cinder_metadata(self):
        metadata = {
            'metadata': unicode("[{'key': 'test', 'value': 'cinder'}]")
        }
        r = FakeReading(metadata=metadata)
        self.assertEquals(metadata_field(self.key, r), 'cinder')


class TestResourceId(unittest.TestCase):
    """Tests the resource_id field function."""
    def test_resource_id(self):
        r = FakeReading()
        self.assertEquals(resource_id(None, None, r), 'resource_id')


class TestPayerAccountId(unittest.TestCase):
    """Tests the payer_account_id field function."""
    def test_payer_account_id(self):
        r = FakeReading()
        self.assertEquals(payer_account_id(None, None, r), 'project_id')


class TestTimeInterval(unittest.TestCase):
    """Tests the timeinterval field function."""
    def test_timeinterval(self):
        stop = datetime.datetime.utcnow()
        start = stop - datetime.timedelta(hours=1)
        r = FakeReading(start=start, stop=stop)
        expected = '{}/{}'.format(start.isoformat(), stop.isoformat())
        self.assertEquals(timeinterval(None, None, r), expected)


class TestInvoiceId(unittest.TestCase):
    """Tests the invoice id field function."""
    def test_invoice_id(self):
        # This function only returns the empty string right now.
        self.assertEquals(invoice_id(None, None, None), '')


class TestBillingEntity(unittest.TestCase):
    """Tests the billing entity field function."""
    def test_billing_entity(self):
        i = {'billing_entity': 'from_item'}
        d = {'billing_entity': 'from_definition'}
        self.assertEquals(billing_entity(d, i, None), 'from_item')
        self.assertEquals(billing_entity(d, {}, None), 'from_definition')


class TestBillingPeriodStartDate(unittest.TestCase):
    """Tests the billing period start date field function."""
    def test_billing_period_start_date(self):
        start = datetime.datetime.utcnow()
        r = FakeReading(start=start)
        self.assertEquals(
            billing_period_start_date(None, None, r),
            start.isoformat()
        )


class TestBillingPeriodEndDate(unittest.TestCase):
    """Tests the billing period end date field function."""
    def test_billing_period_end_date(self):
        stop = datetime.datetime.utcnow()
        r = FakeReading(stop=stop)
        self.assertEquals(
            billing_period_end_date(None, None, r),
            stop.isoformat()
        )


class TestDisplayName(unittest.TestCase):
    """Tests the display name field function."""
    def test_display_name(self):
        r = FakeReading()
        self.assertTrue(display_name(None, None, r) is None)
        r = FakeReading(metadata={'display_name': 'display_name'})
        self.assertEquals(display_name(None, None, r), 'display_name')


class TestInstanceType(unittest.TestCase):
    """Tests the instance type field function."""
    def test_instance_type(self):
        r = FakeReading()
        self.assertTrue(instance_type(None, None, r) is None)
        r = FakeReading(metadata={'instance_type': 'instance_type'})
        self.assertEquals(instance_type(None, None, r), 'instance_type')


class TestUsageAccountId(unittest.TestCase):
    """Tests the usage account id field function."""
    def test_usage_account_id(self):
        r = FakeReading()
        self.assertEquals(usage_account_id(None, None, r), 'project_id')


class TestLineItemType(unittest.TestCase):
    """Tests the line item type field function."""
    def test_line_item_type(self):
        item = {'line_item_type': 'line_item_type'}
        self.assertTrue(line_item_type(None, {}, None) is '')
        self.assertEquals(line_item_type(None, item, None), 'line_item_type')


class TestProductCode(unittest.TestCase):
    """Tests the product code field function."""
    def test_product_code(self):
        item = {'product_code': 'product_code'}
        self.assertTrue(product_code(None, {}, None) is '')
        self.assertEquals(product_code(None, item, None), 'product_code')


class TestProductName(unittest.TestCase):
    """Tests the product name field function."""
    def test_product_name(self):
        item = {'product_name': 'product_name'}
        self.assertTrue(product_name(None, {}, None) is '')
        self.assertEquals(product_name(None, item, None), 'product_name')


class TestUsageType(unittest.TestCase):
    """Tests the usage type field function."""
    def test_usage_type(self):
        item = {'usage_type': 'usage_type'}
        self.assertTrue(usage_type(None, {}, None) is '')
        self.assertEquals(usage_type(None, item, None), 'usage_type')


class TestOperation(unittest.TestCase):
    """Tests the operation field function."""
    def test_operation(self):
        item = {'operation': 'operation'}
        self.assertTrue(operation(None, {}, None) is '')
        self.assertEquals(operation(None, item, None), 'operation')


class TestUsageStartDate(unittest.TestCase):
    """Tests the usage start date field function."""
    def test_usage_start_date(self):
        start = datetime.datetime.utcnow()
        r = FakeReading(start=start)
        self.assertEquals(usage_start_date(None, None, r), start.isoformat())


class TestUsageEndDate(unittest.TestCase):
    """Tests the usage end date field function."""
    def test_usage_end_date(self):
        stop = datetime.datetime.utcnow()
        r = FakeReading(stop=stop)
        self.assertEquals(usage_end_date(None, None, r), stop.isoformat())


class TestAvailabilityZone(unittest.TestCase):
    """Tests the availability zone field function."""
    def test_availability_zone(self):
        metadata = {}
        r = FakeReading(metadata=metadata)
        self.assertTrue(availability_zone(None, None, r) is '')

        metadata = {'availability_zone': 'availability_zone'}
        r = FakeReading(metadata=metadata)
        self.assertEquals(
            availability_zone(None, None, r),
            'availability_zone'
        )


class TestUsageAmount(unittest.TestCase):
    """Tests the usage amount field function."""
    def test_usage_amount(self):
        r = FakeReading()
        self.assertEquals(usage_amount(None, None, r), 'value')


class TestCurrencyCode(unittest.TestCase):
    """Tests the currency code field function."""
    def test_currency_code(self):
        i = {'currency_code': 'from_item'}
        d = {'currency_code': 'from_definition'}
        self.assertTrue(currency_code({}, {}, None) is '')
        self.assertEquals(currency_code(d, i, None), 'from_item')
        self.assertEquals(currency_code(d, {}, None), 'from_definition')


class TestItemRate(unittest.TestCase):
    """Tests the item rate field function."""
    def test_item_rate(self):
        self.assertEquals(item_rate(None, {}, None), 0.0)
        i = {'item_rate': 'item_rate'}
        self.assertEquals(item_rate(None, i, None), 'item_rate')


class TestDescription(unittest.TestCase):
    """Tests the description field function."""
    def test_description(self):
        i = {'description': 'description'}
        self.assertTrue(description(None, {}, None) is '')
        self.assertEquals(description(None, i, None), 'description')
