from setuptools import setup
from usage.meta import version
from usage.meta import description

entry_points = """
    [console_scripts]
    usage-licensing=usage.console:console_licensing
    usage-report=usage.console:console_report
    usage-summary=usage.console:console_summary
    [usage.conversions]
    hours_to_days=usage.conversions.time_units:hours_to_days
    seconds_to_hours=usage.conversions.time_units:seconds_to_hours
    bytes_to_gigabytes=usage.conversions.disk_units:bytes_to_gigabytes
    megabytes_to_gigabytes=usage.conversions.disk_units:megabytes_to_gigabytes
    [usage.fields]
    availability_zone=usage.fields.reading:availability_zone
    billing_entity=usage.fields.item:billing_entity
    billing_period_start_date=usage.fields.reading:billing_period_start_date
    billing_period_end_date=usage.fields.reading:billing_period_end_date
    cost=usage.fields.reading:cost
    currency_code=usage.fields.item:currency_code
    description=usage.fields.item:description
    display_name=usage.fields.reading:display_name
    hours=usage.fields.reading:hours
    instance_type=usage.fields.reading:instance_type
    invoice_id=usage.fields.report:invoice_id
    item_rate=usage.fields.item:item_rate
    line_item_type=usage.fields.item:line_item_type
    meter_name=usage.fields.item:meter_name
    operation=usage.fields.item:operation
    payer_account_id=usage.fields.reading:payer_account_id
    project_id=usage.fields.reading:project_id
    product_code=usage.fields.item:product_code
    product_name=usage.fields.item:product_name
    resource_id=usage.fields.reading:resource_id
    timeinterval=usage.fields.reading:timeinterval
    usage_account_id=usage.fields.reading:usage_account_id
    usage_amount=usage.fields.reading:usage_amount
    usage_end_date=usage.fields.reading:usage_end_date
    usage_start_date=usage.fields.reading:usage_start_date
    usage_type=usage.fields.item:usage_type
    [usage.licensers]
    OracleCount=usage.licensing.oracle:CountLicenser
    OracleHours=usage.licensing.oracle:HourLicenser
    SQLServerCount=usage.licensing.sqlserver:CountLicenser
    SQLServerHours=usage.licensing.sqlserver:HourLicenser
    WindowsHours=usage.licensing.windows:HourLicenser
    WindowsCount=usage.licensing.windows:CountLicenser
"""

setup(
    name="usage",
    version=version,
    author="james absalon",
    author_email="james.absalon@rackspace.com",
    packages=[
        'usage',
        'usage.args',
        'usage.conversions',
        'usage.fields',
        'usage.licensing'
    ],
    entry_points=entry_points,
    package_data={'usage': ['usage/*']},
    long_description=description
)
