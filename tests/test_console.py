import mock
import unittest

from fakes import FakeArgs
from usage.console import console_report


class TestConsoleReport(unittest.TestCase):
    """Tests the Console Report function."""

    @mock.patch('usage.console.logger')
    @mock.patch('usage.console.config')
    @mock.patch('usage.console.ClientManager')
    @mock.patch('usage.console.utils')
    @mock.patch('usage.console.Report')
    @mock.patch('usage.console.parser.parse_args')
    def test_console_report(self,
                            m_args,
                            m_report,
                            m_utils,
                            m_clients,
                            m_config,
                            m_logger):
        m_utils.mtd_range = \
            mock.Mock(return_value=('month_start', 'month_stop'))
        m_utils.today_range = \
            mock.Mock(return_value=('day_start', 'day_stop'))
        m_utils.last_hour_range = \
            mock.Mock(return_value=('last_hour_start', 'last_hour_stop'))

        # Test that mtd is used with no time args
        m_args.return_value = FakeArgs()
        console_report()
        self.assertEquals('month_start', m_report.call_args[1]['start'])
        self.assertEquals('month_stop', m_report.call_args[1]['stop'])

        # Test that mtd is used with mtd set to true
        m_args.return_value = FakeArgs(
            mtd=True, last_hour=True, today=True, start=True, stop=True
        )
        console_report()
        self.assertEquals('month_start', m_report.call_args[1]['start'])
        self.assertEquals('month_stop', m_report.call_args[1]['stop'])

        # Test that today is used with day set to true and mtd false.
        m_args.return_value = FakeArgs(last_hour=True, today=True)
        console_report()
        self.assertEquals('day_start', m_report.call_args[1]['start'])
        self.assertEquals('day_stop', m_report.call_args[1]['stop'])

        # Test that last hour is used when set to true
        m_args.return_value = FakeArgs(last_hour=True)
        console_report()
        self.assertEquals('last_hour_start', m_report.call_args[1]['start'])
        self.assertEquals('last_hour_stop', m_report.call_args[1]['stop'])

        # Test that exception is raised when stop is provided without start
        m_args.return_value = FakeArgs(start=None, stop='stop')
        with self.assertRaises(Exception):
            console_report()

        # Test that start and stop are used when provided
        m_args.return_value = FakeArgs(start='start', stop='stop')
        console_report()
        self.assertEquals('start', m_report.call_args[1]['start'])
        self.assertEquals('stop', m_report.call_args[1]['stop'])

        # Test that stop is defaulted correctly when start is provided
        # without a stop
        m_args.return_value = FakeArgs(start='start', stop=None)
        console_report()
        self.assertEquals('start', m_report.call_args[1]['start'])
        self.assertEquals('month_stop', m_report.call_args[1]['stop'])
