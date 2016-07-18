import unittest

from usage.args.licensing import parser


class TestLicensingArgs(unittest.TestCase):
    """Tests the arg parser."""

    def test_config_file(self):
        test_args = ['somefile']
        args = parser.parse_args(test_args)
        self.assertEquals('/etc/usage/usage.yaml', args.config_file)

        test_args = ['somefile', '--config-file', 'somefile']
        args = parser.parse_args(test_args)
        self.assertEquals('somefile', args.config_file)

    def test_log_level(self):
        test_args = ['somefile']
        args = parser.parse_args(test_args)
        self.assertEquals('info', args.log_level)

        test_args = ['somefile', '--log-level', 'debug']
        args = parser.parse_args(test_args)
        self.assertEquals('debug', args.log_level)

    def test_definition_file(self):
        test_args = ['somefile']
        args = parser.parse_args(test_args)
        self.assertEquals('/etc/usage/licensing.yaml', args.definition_file)

        test_args = ['--definition-file', 'thefile', 'somefile']
        args = parser.parse_args(test_args)
        self.assertEquals('thefile', args.definition_file)
