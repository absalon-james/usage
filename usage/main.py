import config
import conversions
import utils

from args import parser
from clients import ClientManager
from log import logging
from meter import Meter

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO
}

logger = logging.getLogger('usage')
logger.setLevel(logging.INFO)


def report(client, start, stop, measurements):
    logger.info('Reporting for {} to {}'.format(
        start.isoformat(), stop.isoformat()
    ))
    for meter_name, func, units in measurements:
        meter = Meter(client, meter_name)
        # Get reading
        reading = meter.read(start=start, stop=stop)
        # Apply optional conversion
        if func is not None:
            reading = func(reading)
        logger.info('{}: {} {}'.format(meter_name, reading, units))

args = parser.parse_args()
conf = config.load(args.config_file)

logger.setLevel(LOG_LEVELS.get(args.log_level.lower(), 'info'))

clients = ClientManager(**conf.get('auth_kwargs', {}))
client = clients.get_ceilometer()

measurements = [
    ('vcpus', None, 'vcpu hours'),
    ('volume.size', None, 'GB hours'),
    ('image.size', conversions.bytes_to_gigabytes, 'GB Hours'),
    ('disk.write.requests', None, 'requests')
]
measurements.sort(key=lambda i: i[0])

if args.mtd:
    start, stop = utils.mtd_range()
    report(client, start, stop, measurements)

if args.today:
    start, stop = utils.today_range()
    report(client, start, stop, measurements)

if args.last_hour:
    start, stop = utils.last_hour_range()
    report(client, start, stop, measurements)
