import config
import output
import tag
import utils

from args import parser
from clients import ClientManager
from log import logging
from report import Report


LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO
}

logger = logging.getLogger('usage')
logger.setLevel(logging.INFO)


def console_report():
    """Runs a report from the cli."""

    args = parser.parse_args()
    conf = config.load(args.config_file)
    logger.setLevel(LOG_LEVELS.get(args.log_level.lower(), 'info'))

    manager = ClientManager(**conf.get('auth_kwargs', {}))
    ceilometer = manager.get_ceilometer()

    out = output.Stream() if args.use_stdout else None

    if args.mtd:
        start, stop = utils.mtd_range()
        out = out or output.Mtd(args.output_directory, start, stop)
    elif args.today:
        start, stop = utils.today_range()
        out = out or output.Daily(args.output_directory, start, stop)
    elif args.last_hour:
        start, stop = utils.last_hour_range()
        out = out or output.Hourly(args.output_directory, start, stop)

    # If stop is provided, check for start
    elif args.stop:
        if not args.start:
            raise Exception('Provide --start if also using --stop')
        start = args.start
        stop = args.stop
        out = out or output.Other(args.output_directory, start, stop)

    # If start is provided, check for stop. If stop not provided,
    # default to now
    elif args.start:
        start = args.start
        _, now = utils.mtd_range()
        stop = args.stop or now
        out = out or output.Other(args.output_directory, start, stop)

    # Default to month to date
    else:
        start, stop = utils.mtd_range()
        out = out or output.Mtd(args.output_directory, start, stop)
    try:
        r = Report(
            ceilometer,
            args.definition_filename,
            out,
            start=start,
            stop=stop
        )
        r.run()
    finally:
        out.close()

    if args.show_tags:
        print tag.all()
