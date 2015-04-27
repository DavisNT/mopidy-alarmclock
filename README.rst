****************************
Mopidy-AlarmClock
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-AlarmClock.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-AlarmClock/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-AlarmClock.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-AlarmClock/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/DavisNT/mopidy-alarmclock.svg?branch=master
    :target: https://travis-ci.org/DavisNT/mopidy-alarmclock
    :alt: Travis-CI build status

.. image:: https://coveralls.io/repos/DavisNT/mopidy-alarmclock/badge.svg
    :target: https://coveralls.io/r/DavisNT/mopidy-alarmclock
    :alt: Coveralls test coverage

A Mopidy extension for using it as an alarm clock.

Mopidy-AlarmClock was originally created by `Mathieu Xhonneux <https://github.com/Zashas>`_ and now is maintained by `Davis Mosenkovs <https://github.com/DavisNT>`_.

Installation
============

Install by running::

    pip install Mopidy-AlarmClock


Configuration
=============

Alarm defaults can be configured in ``mopidy.conf`` config file::

    [alarmclock]
    # Default alarm time in Hours:Minutes format
    def_time = 8:00

    # Name or Mopidy URI of default alarm playlist
    def_playlist = 

    # Default state of Random Track Order (true or false)
    def_random = false

    # Default alarm volume (integer, 1 to 100)
    def_volume = 100

    # Default seconds to full volume (integer, 0 to 300)
    def_vol_inc_duration = 30


Usage
=============

Make sure that the `HTTP extension <http://docs.mopidy.com/en/latest/ext/http/>`_ is enabled. Then browse to the app on the Mopidy server (for instance, http://localhost:6680/alarmclock/).

Project resources
=================

- `Source code <https://github.com/DavisNT/mopidy-alarmclock>`_
- `Issue tracker <https://github.com/DavisNT/mopidy-alarmclock/issues>`_
- `Development branch tarball <https://github.com/DavisNT/mopidy-alarmclock/archive/master.tar.gz#egg=Mopidy-AlarmClock-dev>`_


Changelog
=========

v0.1.4
----------------------------------------

- Alarm defaults can now be configured in ``mopidy.conf``.
- Display alarm volume on *Alarm state*.
- Display current time of alarm clock on *Alarm state*.
- Added `Travis-CI build <https://travis-ci.org/DavisNT/mopidy-alarmclock>`_ and `Coveralls test coverage info <https://coveralls.io/r/DavisNT/mopidy-alarmclock>`_.
- Fixed README (to be parsable by PyPI).

v0.1.3
----------------------------------------

- Added adjustable volume and gradually increasing volume.
- Fixed stale message appearing on page reload.
- Minor internal code changes and interface changes.
- Updated README/Changelog.

v0.1.2
----------------------------------------

- Fixed alarm starting immediately in some situations.
- Renamed *Shuffle Mode* to *Random Track Order*.

v0.1.1
----------------------------------------

- Project taken over by `Davis Mosenkovs <https://github.com/DavisNT>`_.
- Project moved from `Zashas/mopidy-alarmclock <https://github.com/Zashas/mopidy-alarmclock>`_ to `DavisNT/mopidy-alarmclock <https://github.com/DavisNT/mopidy-alarmclock>`_.
- Fixed setup (+ minor technical fixes).
- Automatically unmute and set volume to 100%.
- Updated Shuffle method.
- Timer resolution is now 5 sec.

v0.1.0 (UNRELEASED)
----------------------------------------

- Created by `Mathieu Xhonneux <https://github.com/Zashas>`_.
- Initial release.
