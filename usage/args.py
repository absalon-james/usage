"""
Module for parsing arguments from the command line.

Import parser from this module.
"""
import argparse
import meta
import utils


def check_datetime(date_str):
    """Parse iso8601 datetime strings.

    :param date_str: String from a datetime argument.
    :type date_str: String
    :returns: Normalized datetime object
    :rtype: datetime.datetime
    """
    try:
        dt = utils.parse_datetime(date_str)
        dt = utils.normalize_time(dt)
    except:
        raise argparse.ArgumentTypeError(
            "{} is an invalid iso8601 datetime string.".format(date_str)
        )
    return dt

parser = argparse.ArgumentParser(description=meta.description)

# Configuration file
parser.add_argument(
    '--config-file', type=str,
    help="Configuration file location",
    default='/etc/usage/usage.yaml'
)

# Version
parser.add_argument(
    '--version', action='version',
    version='%(prog)s ' + str(meta.version)
)

# Include a report for month to date
parser.add_argument(
    '--mtd', action='store_true',
    help='Usage for month to date',
    default=False
)

# Include a report for today
parser.add_argument(
    '--today', action='store_true',
    help="Usage for today",
    default=False
)

# Include a report for the last hour
parser.add_argument(
    '--last-hour', action='store_true',
    help='Usage for last hour',
    default=False
)

# The following are for arbitrary time inputs
parser.add_argument(
    '--start',
    type=check_datetime,
    help="ISO8601 Report Start Date and Time"
)
parser.add_argument(
    '--stop',
    type=check_datetime,
    help="ISO8601 Report Stop Date and Time"
)

# Include an option for filename
parser.add_argument(
    '--definition-filename',
    default='/etc/usage/report.yaml',
    help='Report definition location.'
)

parser.add_argument(
    '--output-directory',
    default='/etc/usage/reports',
    help="Base directory for report outputs."
)

# Set the log level.
parser.add_argument(
    '--log-level', help="Log level", choices=['debug', 'info'],
    default='info'
)

# Set whether or not to show tags
parser.add_argument(
    '--show-tags',
    help="Displays tags and values to stdout",
    default=False,
    action='store_true'
)

# Set whether or not to dump to stdout
parser.add_argument(
    '--use-stdout',
    help='Ouput to stdout instead of file.',
    default=False,
    action="store_true"
)
