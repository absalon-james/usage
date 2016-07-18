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

# Summary definition file
parser.add_argument(
    '--definition-file', type=str,
    help="Location of yaml file defining how to compute licensing cost.",
    default='/etc/usage/licensing.yaml'
)
