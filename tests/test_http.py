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

        alarm_manager.set_alarm.assert_called_once_with(datetime.datetime(2015, 5, 3, 8, 0), 'Playlist URI', True, 81, 23)
        self.assertEqual(msg_store.msg_code, 'ok')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 2 - defaults, time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '05:7', 'random': d, 'volume': d, 'incsec': d}[v]

        handler.post()

        # WARNING! Default configuration must be also updated in README.rst and ext.conf
        # WARNING! Internal defaults of volume and volume increase seconds are in SetAlarmRequestHandler of http.py
        alarm_manager.set_alarm.assert_called_once_with(datetime.datetime(2015, 5, 4, 5, 7), 'Playlist URI', False, 100, 30)
        self.assertEqual(msg_store.msg_code, 'ok')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 3 - ranges, time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '23:59', 'random': '1', 'volume': '0', 'incsec': '-1'}[v]

        handler.post()

        # WARNING! Default configuration (AND RANGES) must be also updated in README.rst and ext.conf
        # WARNING! Internal defaults of volume and volume increase seconds are in SetAlarmRequestHandler of http.py
        # WARNING! Ranges of volume and volume increase seconds are in SetAlarmRequestHandler of http.py AND HTML form of index.html
        alarm_manager.set_alarm.assert_called_once_with(datetime.datetime(2015, 5, 3, 23, 59), 'Playlist URI', True, 100, 30)
        self.assertEqual(msg_store.msg_code, 'ok')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 4 - ranges, time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '0:0', 'random': '1', 'volume': '101', 'incsec': '301'}[v]

        handler.post()

        # WARNING! Default configuration (AND RANGES) must be also updated in README.rst and ext.conf
        # WARNING! Internal defaults of volume and volume increase seconds are in SetAlarmRequestHandler of http.py
        # WARNING! Ranges of volume and volume increase seconds are in SetAlarmRequestHandler of http.py AND HTML form of index.html
        alarm_manager.set_alarm.assert_called_once_with(datetime.datetime(2015, 5, 4, 0, 0), 'Playlist URI', True, 100, 30)
        self.assertEqual(msg_store.msg_code, 'ok')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 5 - invalid time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': 'a8:00', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)
        self.assertEqual(msg_store.msg_code, 'format')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 6 - invalid time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '8:00a', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)
        self.assertEqual(msg_store.msg_code, 'format')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 7 - invalid time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '8:0a0', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)
        self.assertEqual(msg_store.msg_code, 'format')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 8 - invalid time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '800', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)
        self.assertEqual(msg_store.msg_code, 'format')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 9 - invalid time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '8_00', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)
        self.assertEqual(msg_store.msg_code, 'format')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 10 - invalid time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)
        self.assertEqual(msg_store.msg_code, 'format')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 11 - invalid time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': 'a', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)
        self.assertEqual(msg_store.msg_code, 'format')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 12 - invalid time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '24:00', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)
        self.assertEqual(msg_store.msg_code, 'format')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 13 - invalid time format
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': '8:60', 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)
        self.assertEqual(msg_store.msg_code, 'format')
        handler.redirect.assert_called_once_with('/alarmclock/')

        # Cleanup
        alarm_manager.reset_mock()
        handler.redirect.reset_mock()
        msg_store.msg_code = None

        # Test 14 - missing time
        handler.get_argument.side_effect = lambda v, d: {'playlist': 'Playlist URI', 'time': d, 'random': '1', 'volume': '81', 'incsec': '23'}[v]

        with self.assertRaises(TypeError):
            handler.post()

        self.assertFalse(alarm_manager.set_alarm.called)

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
