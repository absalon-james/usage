import unittest

from usage.args.summary import parser


class TestArgs(unittest.TestCase):
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

    def test_group_by(self):
        test_args = ['somefile']
        args = parser.parse_args(test_args)
        self.assertEquals('user:appid', args.group_by)

        test_args = ['somefile', '--group-by', 'something']
        args = parser.parse_args(test_args)
        self.assertEquals('something', args.group_by)

    def test_project_id_field(self):
        test_args = ['somefile']
        args = parser.parse_args(test_args)
        self.assertEquals('Project Id', args.project_id_field)

        test_args = ['somefile', '--project-id-field', 'something']
        args = parser.parse_args(test_args)
        self.assertEquals('something', args.project_id_field)

    def test_cost_field(self):
        test_args = ['somefile']
        args = parser.parse_args(test_args)
        self.assertEquals('Cost', args.cost_field)

        test_args = ['somefile', '--cost-field', 'something']
        args = parser.parse_args(test_args)
        self.assertEquals('something', args.cost_field)
