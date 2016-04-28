import config
import conversions
import utils

from args import parser
from clients import ClientManager
from log import logging
from meter import Meter
from report import Report

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO
}

logger = logging.getLogger('usage')
logger.setLevel(logging.INFO)

args = parser.parse_args()
conf = config.load(args.config_file)
logger.setLevel(LOG_LEVELS.get(args.log_level.lower(), 'info'))

manager = ClientManager(**conf.get('auth_kwargs', {}))
ceilometer = manager.get_ceilometer()

if args.mtd:
    start, stop = utils.mtd_range()
elif args.today:
    start, stop = utils.today_range()
elif args.last_hour:
    start, stop = utils.last_hour_range()
else:
    start, stop = utils.mtd_range()

r = Report(
    ceilometer,
    args.definition_filename,
    args.csv_filename,
    start=start,
    stop=stop
)
r.run()
