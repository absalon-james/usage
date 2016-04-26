"""
Module for parsing arguments from the command line.

Import parser from this module.
"""
import argparse
import meta


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

# Set the log level.
parser.add_argument(
    '--log-level', help="Log level", choices=['debug', 'info'],
    default='info'
)
