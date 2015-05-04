from __future__ import unicode_literals

import datetime
import unittest

from freezegun import freeze_time

import mock

from mopidy_alarmclock import http


class HttpTest(unittest.TestCase):

    @freeze_time("2015-05-03 07:17:53")
    def test_SetAlarmRequestHandler(self):
        config = mock.Mock()
        core = mock.Mock()
        alarm_manager = mock.Mock()
        msg_store = mock.Mock()

        patcher = mock.patch.object(http.SetAlarmRequestHandler, '__bases__', (mock.Mock,))
        with patcher:
            patcher.is_local = True
            handler = http.SetAlarmRequestHandler()

        handler.initialize(config, core, alarm_manager, msg_store)
        handler.redirect = mock.Mock()
        handler.get_argument = mock.Mock()
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '8:00', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertEqual(alarm_manager.set_alarm.call_count, 1)
        alarm_manager.set_alarm.assert_called_once_with(datetime.datetime(2015, 05, 03, 8, 0), core.playlists.lookup('Playlist URI').get(), True, 81, 23)

    # TODO Use Tornado unit testing
    # TODO Write more (granular + comprehensive) tests
