"""
Module for parsing configuration files.

Configuration files should be yaml.
"""
import yaml


def load(filename):
    """Load a dictionary from a yaml file.

    Expects the file at filename to be a yaml file.
    Returns the parsed configuration as a dictionary.

    :param filename: Name of the file
    :type filename: String
    :return: Loaded configuration
    :rtype: Dict
    """
    with open(filename, 'r') as f:
        return yaml.load(f)
