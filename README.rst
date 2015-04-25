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

Mopidy-AlarmClock was originally created by `Mathieu Xhonneux <https://github.com/Zashas>`_ and now is maintained by `Davis Mosenkovs <https://github.com/DavisNT>`_.

Installation
============

Install by running::

    pip install Mopidy-AlarmClock


Configuration
=============

This extension requires no configuration.

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
- Project moved from `Zashas <https://github.com/Zashas>`_/`mopidy-alarmclock <https://github.com/Zashas/mopidy-alarmclock>`_ to `DavisNT <https://github.com/DavisNT>`_/`mopidy-alarmclock <https://github.com/DavisNT/mopidy-alarmclock>`_
- Fixed setup (+ minor technical fixes).
- Automatically unmute and set volume to 100%.
- Updated Shuffle method.
- Timer resolution is now 5 sec.

v0.1.0 (UNRELEASED)
----------------------------------------

- Created by `Mathieu Xhonneux <https://github.com/Zashas>`_.
- Initial release.
