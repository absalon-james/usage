from setuptools import setup
from usage.meta import version
from usage.meta import description

setup(
    name="usage",
    version=version,
    author="james absalon",
    author_email="james.absalon@rackspace.com",
    packages=[
        'usage'
    ],
    package_data={'usage': ['usage/*']},
    long_description=description
)
