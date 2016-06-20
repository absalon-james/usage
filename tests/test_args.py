import datetime
import unittest

from usage.args import parser


class TestArgs(unittest.TestCase):
    """Tests the arg parser."""

    def test_config_file(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertEquals('/etc/usage/usage.yaml', args.config_file)

        test_args = ['--config-file', 'somefile']
        args = parser.parse_args(test_args)
        self.assertEquals('somefile', args.config_file)

    def test_mtd(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertFalse(args.mtd)

        test_args = ['--mtd']
        args = parser.parse_args(test_args)
        self.assertTrue(args.mtd)

    def test_today(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertFalse(args.today)

        test_args = ['--today']
        args = parser.parse_args(test_args)
        self.assertTrue(args.today)

    def test_last_hour(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertFalse(args.last_hour)

        test_args = ['--last-hour']
        args = parser.parse_args(test_args)
        self.assertTrue(args.last_hour)

    def test_start(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertFalse(args.start)

        # This causes the following to exit. not sure how to test.
        # test_args = ['--start', 'notadatetime']
        # with self.assertRaises(ArgumentTypeError):
        #    args = parser.parse_args(test_args)

        test_args = ['--start', '2016-06-01 00:00:00']
        args = parser.parse_args(test_args)
        self.assertTrue(isinstance(args.start, datetime.datetime))

    def test_stop(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertFalse(args.stop)

        # This causes the following to exit. not sure how to test.
        # test_args = ['--stop', 'notadatetime']
        # with self.assertRaises(ArgumentTypeError):
        #    args = parser.parse_args(test_args)

        test_args = ['--stop', '2016-06-01 00:00:00']
        args = parser.parse_args(test_args)
        self.assertTrue(isinstance(args.stop, datetime.datetime))

    def test_definition_filename(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertEquals('/etc/usage/report.yaml', args.definition_filename)

        test_args = ['--definition-filename', 'afile']
        args = parser.parse_args(test_args)
        self.assertEquals('afile', args.definition_filename)

    def test_csv_filename(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertEquals('/etc/usage/reports/billing.csv', args.csv_filename)

        test_args = ['--csv-filename', 'thefile']
        args = parser.parse_args(test_args)
        self.assertEquals('thefile', args.csv_filename)

    def test_log_level(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertEquals('info', args.log_level)

        test_args = ['--log-level', 'debug']
        args = parser.parse_args(test_args)
        self.assertEquals('debug', args.log_level)

    def test_show_tags(self):
        test_args = []
        args = parser.parse_args(test_args)
        self.assertFalse(args.show_tags)

        test_args = ['--show-tags']
        args = parser.parse_args(test_args)
        self.assertTrue(args.show_tags)
