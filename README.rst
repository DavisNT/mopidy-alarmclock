****************************
Mopidy-AlarmClock
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-AlarmClock.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-AlarmClock/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-AlarmClock.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-AlarmClock/
    :alt: Number of PyPI downloads

A Mopidy extension for using it as an alarm clock.


Installation
============

Install by running::

    pip install Mopidy-AlarmClock


Configuration
=============

This extension requires no configuration.

Usage
=============

Make sure that the [HTTP extension](http://docs.mopidy.com/en/latest/ext/http/) is enabled. Then browse to the app on the Mopidy server (for instance, http://localhost:6680/alarmclock/).

Project resources
=================

- `Source code <https://github.com/Zashas/mopidy-alarmclock>`_
- `Issue tracker <https://github.com/Zashas/mopidy-alarmclock/issues>`_
- `Development branch tarball <https://github.com/Zashas/mopidy-alarmclock/archive/master.tar.gz#egg=Mopidy-AlarmClock-dev>`_


Changelog
=========

v0.1.1
----------------------------------------

- Fixed setup (+ minor technical fixes).
- Automatically unmute and set volume to 100%.
- Updated Shuffle method.
- Timer resolution is now 5 sec.

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
