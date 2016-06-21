import os
import sys


class Stream:
    """Stdout output."""
    def __init__(self):
        """Set stream to stdout."""
        self.stream = sys.stdout

    def close(self):
        """Do nothing."""
        pass

    @property
    def location(self):
        return 'stdout'


class File(object):
    """Base class for a file output."""
    def __init__(self, name):
        """Init the file output.

        :param name: Name of the file
        :type name: String
        """
        self.abs_name = os.path.abspath(name)
        self.ensure_directory()
        self.stream = open(self.abs_name, 'w')

    def ensure_directory(self):
        """Make sure the directory exists."""
        directory = os.path.dirname(self.abs_name)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def close(self):
        """Close the file."""
        self.stream.close()

    @property
    def location(self):
        """Get the location of the output.

        :returns: Location of the output.
        :rtype: String
        """
        return self.abs_name


class Mtd(File):
    """Mtd file output class."""
    def __init__(self, basedir, start, stop):
        """Creates the name of the file then supers.

        Filename will be:
        <basedir>/mtd/<year>_<month>.csv

        :param basedir: Base directory
        :type basedir: String
        :param start: Datetime start
        :type start: datetime.datetime
        :param stop: Datetime stop
        :type stop: datetime.datetime
        """
        name = 'mtd/{}_{:02d}.csv'.format(stop.year, stop.month)
        name = os.path.join(basedir, name)
        super(Mtd, self).__init__(name)


class Daily(File):
    """Daily file output class."""
    def __init__(self, basedir, start, stop):
        """Creates the name of the file then supers.

        Filename will be:
        <basedir>/daily/<year>_<month>_<day>.csv

        :param basedir: Base directory
        :type basedir: String
        :param start: Datetime start
        :type start: datetime.datetime
        :param stop: Datetime stop
        :type stop: datetime.datetime
        """
        name = "daily/{}_{:02d}_{:02d}.csv".format(
            stop.year,
            stop.month,
            stop.day
        )
        name = os.path.join(basedir, name)
        super(Daily, self).__init__(name)


class Hourly(File):
    """Hourly file output class."""
    def __init__(self, basedir, start, stop):
        """Creates the name of the file then supers.

        Filename will be:
        <basedir>/hourly/<year>/<month>/<day>/<start time>_to_<stop_time>.csv

        :param basedir: Base directory
        :type basedir: String
        :param start: Datetime start
        :type start: datetime.datetime
        :param stop: Datetime stop
        :type stop: datetime.datetime
        """
        name = 'hourly/{}/{:02d}/{:02d}/{}_to_{}.csv'.format(
            stop.year,
            stop.month,
            stop.day,
            start.isoformat().split('T')[1],
            stop.isoformat().split('T')[1]
        )
        name = os.path.join(basedir, name)
        super(Hourly, self).__init__(name)


class Other(File):
    """File output for arbitrary time ranges."""
    def __init__(self, basedir, start, stop):
        """Creates the name of the file then supers.

        Filename will be:
        <basedir>/other/<start datetime>_to_<stop_datetime>.csv

        :param basedir: Base directory
        :type basedir: String
        :param start: Datetime start
        :type start: datetime.datetime
        :param stop: Datetime stop
        :type stop: datetime.datetime
        """
        name = 'other/{}_to_{}.csv'.format(
            start.isoformat(),
            stop.isoformat()
        )
        name = os.path.join(basedir, name)
        super(Other, self).__init__(name)
