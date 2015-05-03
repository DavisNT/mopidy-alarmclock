from __future__ import unicode_literals

import unittest

import mock

from mopidy_alarmclock import http


class HttpTest(unittest.TestCase):

    @mock.patch('mopidy_alarmclock.http.tornado')
    def test_SetAlarmRequestHandler(self):
        config = mock.Mock()
        core = mock.Mock()
        alarm_manager = mock.Mock()
        msg_store = mock.Mock()

        handler = http.SetAlarmRequestHandler()
        handler.initialize(config, core, alarm_manager, msg_store)
        handler.get_argument = mock.Mock()
        handler.get_argument.side_effect = lambda v: {'playlist': 'Playlist URI', 'time': '8:00', 'random': '1', 'volume': '81', 'incsec': '23'}[v]
        handler.post()

        self.assertEqual(alarm_manager.set_alarm.call_count, 1)
        self.assertEqual(alarm_manager.set_alarm.call_args[0][1], core.playlists.lookup('Playlist URI').get())
        self.assertEqual(alarm_manager.set_alarm.call_args[0][2], True)
        self.assertEqual(alarm_manager.set_alarm.call_args[0][3], 81)
        self.assertEqual(alarm_manager.set_alarm.call_args[0][4], 23)

    # TODO Use Tornado unit testing
    # TODO Write more (granular + comprehensive) tests
