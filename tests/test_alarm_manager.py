from __future__ import unicode_literals

import datetime
import time
import unittest

import mock

from mopidy_alarmclock.alarm_manager import AlarmManager


class AlarmManagerTest(unittest.TestCase):

    def test_get_seconds_since_midnight(self):
        am = AlarmManager()

        seconds = am.get_seconds_since_midnight()

        self.assertIsInstance(seconds, int)
        self.assertTrue(seconds >= 0 and seconds < 86400)

    def integration_test_1(self):
        core = mock.Mock()
        playlist = mock.Mock()
        playlist.tracks = 'Tracks 811, 821, 823, 827, 829, 839'

        am = AlarmManager()

        # Test get_core()
        self.assertTrue(am is am.get_core(core))

        # Test is_set() when NOT set
        self.assertFalse(am.is_set())

        # Set alarm to FAR future
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        # Test when set
        self.assertTrue(am.is_set())
        self.assertEqual(am.get_ring_time(), b'07:59')
        self.assertFalse(am.random_mode)
        self.assertEqual(am.volume, 41)
        self.assertEqual(am.volume_increase_seconds, 83)

        # Cancel alarm
        am.cancel()
        time.sleep(7)  # Sleep a little longer than timer-resolution (to prevent several simultaneous timers)
        # TODO Fix this issue in the code

        # Test is_set() when NOT set
        self.assertFalse(am.is_set())

        # Set alarm to NEAR future
        am.set_alarm(datetime.datetime.now() + datetime.timedelta(seconds=29), playlist, False, 23, 127)

        # Tests a few seconds BEFORE alarm
        time.sleep(27)
        self.assertTrue(am.is_set())
        self.assertFalse(am.random_mode)
        self.assertEqual(am.volume, 23)
        self.assertEqual(am.volume_increase_seconds, 127)

        # Cancel alarm
        am.cancel()
        time.sleep(7)  # Sleep a little longer than timer-resolution (to prevent several simultaneous timers)
        # TODO Fix this issue in the code

        # Test is_set() when NOT set
        self.assertFalse(am.is_set())

        # Sleep 20 seconds more to ensure that alarm will start if not cancelled
        time.sleep(20)

        # Set alarm to NEAR future
        am.set_alarm(datetime.datetime.now() + datetime.timedelta(seconds=31), playlist, True, 3, 17)

        # Test when set
        self.assertTrue(am.is_set())
        self.assertTrue(am.random_mode)
        self.assertEqual(am.volume, 3)
        self.assertEqual(am.volume_increase_seconds, 17)

        # Tests a few seconds BEFORE alarm
        time.sleep(29)
        self.assertTrue(am.is_set())
        self.assertIsInstance(core.tracklist.repeat, mock.Mock)
        self.assertIsInstance(core.tracklist.random, mock.Mock)
        self.assertIsInstance(core.playback.mute, mock.Mock)
        self.assertIsInstance(core.playback.volume, mock.Mock)
        self.assertEqual(core.playback.stop.call_count, 0)
        self.assertEqual(core.tracklist.clear.call_count, 0)
        self.assertEqual(core.tracklist.add.call_count, 0)
        self.assertEqual(core.playback.next.call_count, 0)
        self.assertEqual(core.playback.play.call_count, 0)

        # Tests a few seconds AFTER alarm START
        time.sleep(8)
        self.assertFalse(am.is_set())
        self.assertEqual(core.tracklist.repeat, True)
        self.assertEqual(core.tracklist.random, True)
        self.assertEqual(core.playback.mute, False)
        self.assertEqual(core.playback.volume, 1)  # First step of gradual volume increasing
        self.assertEqual(core.playback.stop.call_count, 1)
        self.assertEqual(core.tracklist.clear.call_count, 1)
        self.assertEqual(core.tracklist.add.call_count, 1)
        core.tracklist.add.assert_called_once_with('Tracks 811, 821, 823, 827, 829, 839')
        self.assertEqual(core.playback.next.call_count, 1)
        self.assertEqual(core.playback.play.call_count, 1)

        # Further tests of gradual volume increasing
        time.sleep(5.67)
        self.assertEqual(core.playback.volume, 2)
        time.sleep(5.67)
        self.assertEqual(core.playback.volume, 2)
        time.sleep(5.67)
        self.assertEqual(core.playback.volume, 3)
        time.sleep(20)  # More than 3x increase step time
        self.assertEqual(core.playback.volume, 3)

    # TODO Write more (granular + comprehensive) tests
