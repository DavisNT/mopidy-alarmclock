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
        msg_store = http.MessageStore()

        patcher = mock.patch.object(http.SetAlarmRequestHandler, '__bases__', (mock.Mock,))
        with patcher:
            patcher.is_local = True
            handler = http.SetAlarmRequestHandler()

        handler.initialize(config, core, alarm_manager, msg_store)
        handler.redirect = mock.Mock()
        handler.get_argument = mock.Mock()

        # Test 1
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '8:00', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        alarm_manager.set_alarm.assert_called_once_with(datetime.datetime(2015, 05, 03, 8, 0), core.playlists.lookup('Playlist URI').get(), True, 81, 23)
        self.assertEqual(msg_store.msg_code, 'ok')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 2
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '05:7', 'random': d, 'volume': d, 'incsec': d}[v]

        handler.post()

        alarm_manager.set_alarm.assert_called_once_with(datetime.datetime(2015, 05, 04, 5, 7), core.playlists.lookup('Playlist URI').get(), False, 100, 30)
        self.assertEqual(msg_store.msg_code, 'ok')
        handler.redirect.assert_called_once_with('/alarmclock/')

    def test_CancelAlarmRequestHandler(self):
        alarm_manager = mock.Mock()
        msg_store = http.MessageStore()

        patcher = mock.patch.object(http.CancelAlarmRequestHandler, '__bases__', (mock.Mock,))
        with patcher:
            patcher.is_local = True
            handler = http.CancelAlarmRequestHandler()

        handler.initialize(None, None, alarm_manager, msg_store)
        handler.redirect = mock.Mock()

        handler.get()

        alarm_manager.cancel.assert_called_once_with()
        self.assertEqual(msg_store.msg_code, 'cancel')
        handler.redirect.assert_called_once_with('/alarmclock/')

    # TODO Use Tornado unit testing
    # TODO Write more (granular + comprehensive) tests
