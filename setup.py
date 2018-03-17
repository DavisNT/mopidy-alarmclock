from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-AlarmClock',
    version=get_version('mopidy_alarmclock/__init__.py'),
    url='https://github.com/DavisNT/mopidy-alarmclock',
    license='Apache License, Version 2.0',
    author='Mathieu Xhonneux',
    author_email='m.xhonneux@gmail.com',
    maintainer='Davis Mosenkovs',
    maintainer_email='python-apps@dm.id.lv',
    description='A Mopidy extension for using it as an alarm clock.',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 0.19',
        'Pykka >= 1.1',
        'monotonic >= 1.4',
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'mock >= 1.0',
    ],
    entry_points={
        'mopidy.ext': [
            'alarmclock = mopidy_alarmclock:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
