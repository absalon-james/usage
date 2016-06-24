"""
Module for parsing arguments from the command line.

Import parser from this module.
"""
import argparse

from usage import meta

description = (
    'Python tool for aggregating a usage report by domain'
    ' and some user defined field.'
)
parser = argparse.ArgumentParser(description=description)

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

# Set the log level.
parser.add_argument(
    '--log-level', help="Log level", choices=['debug', 'info'],
    default='info'
)

# Input file location
parser.add_argument('csv_file', help="Location of report csv file.", type=str)

# Field in report to group by
parser.add_argument(
    '--group-by', type=str, default='user:appid',
    help='Column in report to aggregate by in a domain.'
)

# Field that contains the project id
parser.add_argument(
    '--project-id-field', type=str, default='Project Id',
    help=(
        'Column in report containing the project id. The project id is used to'
        ' determine the domain of a resource.'
    )
)

# Field that contains the cost
parser.add_argument(
    '--cost-field', type=str, default='Cost',
    help='Column in report containing the cost.'
)
