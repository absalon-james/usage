import datetime
import mock
import sys
import unittest

from usage import output


class TestStream(unittest.TestCase):
    def test_init(self):
        out = output.Stream()
        self.assertEquals(sys.stdout, out.stream)

    def test_location(self):
        out = output.Stream()
        self.assertEquals('stdout', out.location)


class TestFile(unittest.TestCase):
    @mock.patch('usage.output.os.makedirs')
    @mock.patch('usage.output.open')
    def test_init(self, m_open, m_makedirs):
        name = '/somewhere/somefile.csv'
        f = output.File(name)
        self.assertEquals(name, f.abs_name)
        self.assertEquals(name, f.location)
        m_open.assert_called_with(name, 'w')


class TestMtd(unittest.TestCase):
    @mock.patch('usage.output.File')
    @mock.patch('usage.output.os.makedirs')
    @mock.patch('usage.output.open')
    def test_init(self, m_open, m_makedirs, m_file):
        year = 2016
        month = 1
        day = 2
        stop = datetime.datetime(year=year, month=month, day=day)
        basedir = '/basedir'
        out = output.Mtd(basedir, 'start', stop)
        self.assertEquals(out.location, '/basedir/mtd/2016_01.csv')


class TestDaily(unittest.TestCase):
    @mock.patch('usage.output.File')
    @mock.patch('usage.output.os.makedirs')
    @mock.patch('usage.output.open')
    def test_init(self, m_open, m_makedirs, m_file):
        year = 2016
        month = 1
        day = 2
        stop = datetime.datetime(year=year, month=month, day=day)
        basedir = '/basedir'
        out = output.Daily(basedir, 'start', stop)
        self.assertEquals(out.location, '/basedir/daily/2016_01_02.csv')


class TestOther(unittest.TestCase):
    @mock.patch('usage.output.File')
    @mock.patch('usage.output.os.makedirs')
    @mock.patch('usage.output.open')
    def test_init(self, m_open, m_makedirs, m_file):
        stop = datetime.datetime.utcnow()
        start = stop - datetime.timedelta(hours=1)
        basedir = '/basedir'
        out = output.Other(basedir, start, stop)
        expected = '/basedir/other/{}_to_{}.csv'.format(
            start.isoformat(),
            stop.isoformat()
        )
        self.assertEquals(out.location, expected)
