import datetime
import os
import threading
import time
import unittest

import mock

from mopidy.core import PlaybackState

from mopidy_alarmclock.alarm_manager import AlarmManager


class AlarmManagerTest(unittest.TestCase):

    def test01_get_core(self):
        core = 'This core should crash on play'

        am = AlarmManager()

        self.assertTrue(am is am.get_core(core))

    def test01_get_seconds_since_midnight(self):
        am = AlarmManager()

        seconds = am.get_seconds_since_midnight()

        self.assertIsInstance(seconds, int)
        self.assertTrue(seconds >= 0 and seconds < 86400)

    def test02_is_set(self):
        playlist = 'Playlist URI'

        am = AlarmManager()

        self.assertFalse(am.is_set())

        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        self.assertTrue(am.is_set())

        am.cancel()

        self.assertFalse(am.is_set())

    def test02_set_alarm__threading(self):
        playlist = 'Playlist URI'
        threadcount = threading.active_count()

        am = AlarmManager()

        self.assertEqual(threading.active_count(), threadcount)

        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        self.assertEqual(threading.active_count(), threadcount + 1)

        am.cancel()

        self.assertEqual(threading.active_count(), threadcount)

        # Set alarm twice
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        self.assertEqual(threading.active_count(), threadcount + 1)

        am.cancel()

        self.assertEqual(threading.active_count(), threadcount)

        # Set alarm 3 times
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)
        time.sleep(8)
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        self.assertEqual(threading.active_count(), threadcount + 1)

        am.cancel()

        self.assertEqual(threading.active_count(), threadcount)

        # Set alarm 5 times
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)
        time.sleep(8)
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        self.assertEqual(threading.active_count(), threadcount + 1)

        am.cancel()

        self.assertEqual(threading.active_count(), threadcount)

    def test02_set_alarm__empty_playlist(self):
        core = mock.Mock()
        playlist = 'Playlist URI'
        core.playback.get_state().get.side_effect = lambda: PlaybackState.PLAYING
        core.playback.get_time_position().get.side_effect = lambda: 234
        core.playlists.lookup('Playlist URI').get().tracks = 'Tracks 811, 821, 823, 827, 829, 839'
        core.tracklist.get_length().get.side_effect = lambda: 4
        self.assertEqual(core.playlists.lookup.call_count, 1)  # First call when setting up the Mock

        am = AlarmManager()
        am.get_core(core)

        # Set alarm to PAST
        am.set_alarm(datetime.datetime(2000, 4, 28, 7, 59, 15, 324341), playlist, False, 83, 0)

        # Ensure that tracks were added
        self.assertEqual(core.playlists.lookup.call_count, 2)
        core.tracklist.add.assert_called_once_with('Tracks 811, 821, 823, 827, 829, 839')
        core.playback.play.assert_called_once_with()

        # Cleanup and re-setup
        core.tracklist.add.reset_mock()
        core.playback.play.reset_mock()
        core.tracklist.get_length().get.side_effect = lambda: 0  # Simulate empty play queue

        # Set alarm to PAST
        am.set_alarm(datetime.datetime(2000, 4, 28, 7, 59, 15, 324341), playlist, False, 83, 0)

        # Ensure that tracks (including backup alarm) were added
        self.assertEqual(core.playlists.lookup.call_count, 3)
        self.assertEqual(core.tracklist.add.call_count, 2)
        core.tracklist.add.assert_any_call('Tracks 811, 821, 823, 827, 829, 839')
        core.tracklist.add.assert_called_with(None, 0, ['file://' + os.path.dirname(os.path.dirname(__file__)) + '/mopidy_alarmclock/backup-alarm.mp3'])
        core.playback.play.assert_called_once_with()

    def test02_set_alarm__broken_playback(self):
        core = mock.Mock()
        playlist = 'Playlist URI'
        core.playback.get_state().get.side_effect = lambda: PlaybackState.PLAYING
        core.playback.get_time_position().get.side_effect = lambda: 234
        core.playlists.lookup('Playlist URI').get().tracks = 'Tracks 811, 821, 823, 827, 829, 839'
        core.tracklist.get_length().get.side_effect = lambda: 4
        self.assertEqual(core.playlists.lookup.call_count, 1)  # First call when setting up the Mock

        am = AlarmManager()
        am.get_core(core)

        # Set alarm to PAST
        am.set_alarm(datetime.datetime(2000, 4, 28, 7, 59, 15, 324341), playlist, False, 83, 0)

        # Ensure that tracks were added
        self.assertEqual(core.playlists.lookup.call_count, 2)
        core.tracklist.add.assert_called_once_with('Tracks 811, 821, 823, 827, 829, 839')
        core.playback.play.assert_called_once_with()

        # Cleanup and re-setup (part 2 starts here)
        core.tracklist.add.reset_mock()
        core.playback.play.reset_mock()
        core.playback.get_state().get.reset_mock()
        core.playback.get_time_position().get.reset_mock()
        core.playback.get_state().get.side_effect = lambda: PlaybackState.PLAYING
        core.playback.get_time_position().get.side_effect = lambda: 0  # simulate broken playback (stuck at 0 milliseconds)

        # Set alarm to PAST
        am.set_alarm(datetime.datetime(2000, 4, 28, 7, 59, 15, 324341), playlist, False, 83, 0)

        # Ensure that tracks (including backup alarm) were added and playback started
        self.assertEqual(core.playlists.lookup.call_count, 3)
        self.assertEqual(core.tracklist.add.call_count, 2)
        core.tracklist.add.assert_any_call('Tracks 811, 821, 823, 827, 829, 839')
        core.tracklist.add.assert_called_with(None, 0, ['file://' + os.path.dirname(os.path.dirname(__file__)) + '/mopidy_alarmclock/backup-alarm.mp3'])
        self.assertEqual(core.playback.play.call_count, 2)

        # Ensure playback was checked around 31 times (tolerate 1 sec possible slowness of build env)
        self.assertGreaterEqual(core.playback.get_state().get.call_count, 30)
        self.assertLess(core.playback.get_state().get.call_count, 32)
        self.assertGreaterEqual(core.playback.get_time_position().get.call_count, 30)
        self.assertLess(core.playback.get_time_position().get.call_count, 32)

        # Cleanup and re-setup (part 3 starts here)
        core.tracklist.add.reset_mock()
        core.playback.play.reset_mock()
        core.playback.get_state().get.reset_mock()
        core.playback.get_time_position().get.reset_mock()
        core.playback.get_state().get.side_effect = lambda: time.sleep(31)  # simulate broken playback (return invalid state after 31 second delay)
        core.playback.get_time_position().get.side_effect = lambda: 234

        # Set alarm to PAST
        am.set_alarm(datetime.datetime(2000, 4, 28, 7, 59, 15, 324341), playlist, False, 83, 0)

        # Ensure that tracks (including backup alarm) were added and playback started
        self.assertEqual(core.playlists.lookup.call_count, 4)
        self.assertEqual(core.tracklist.add.call_count, 2)
        core.tracklist.add.assert_any_call('Tracks 811, 821, 823, 827, 829, 839')
        core.tracklist.add.assert_called_with(None, 0, ['file://' + os.path.dirname(os.path.dirname(__file__)) + '/mopidy_alarmclock/backup-alarm.mp3'])
        self.assertEqual(core.playback.play.call_count, 2)

        # Ensure playback was checked exactly 2 times (due to delay during checking)
        self.assertEqual(core.playback.get_state().get.call_count, 2)
        self.assertEqual(core.playback.get_time_position().get.call_count, 0)  # actually this does not get called (because it is 2 operand in or)

    def test02_get_ring_time(self):
        playlist = 'Playlist URI'

        am = AlarmManager()

        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        self.assertEqual(am.get_ring_time(), '07:59')

        am.cancel()

    def test03_cancel(self):
        core = mock.Mock()
        playlist = 'Playlist URI'
        core.playback.get_state().get.side_effect = lambda: PlaybackState.PLAYING
        core.playback.get_time_position().get.side_effect = lambda: 234
        threadcount = threading.active_count()

        am = AlarmManager()
        am.get_core(core)

        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

        # Cancel when alarm is NOT set
        am.cancel()

        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

        # Set alarm to FAR future
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        self.assertTrue(am.is_set())
        self.assertEqual(threading.active_count(), threadcount + 1)

        # Cancel alarm
        am.cancel()

        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

        # Cancel when alarm is already cancelled
        am.cancel()

        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

        # Ensure that alarm has not started (incomplete test)
        self.assertEqual(core.playback.play.call_count, 0)
        self.assertEqual(core.mixer.set_volume.call_count, 0)

        # Set alarm to PAST
        am.set_alarm(datetime.datetime(2000, 4, 28, 7, 59, 15, 324341), playlist, False, 83, 0)

        # Ensure that alarm went off (incomplete test)
        core.playback.play.assert_called_once_with()
        core.mixer.set_volume.assert_called_with(83)

        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

        # Cancel after alarm has been started
        am.cancel()
        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

    def test03_adjust_volume__100_1(self):
        core = mock.Mock()
        threadcount = threading.active_count()

        am = AlarmManager()
        am.get_core(core)

        self.assertEqual(threading.active_count(), threadcount)

        am.adjust_volume(100, 1, 0)

        core.mixer.set_volume.assert_called_once_with(50)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(1.2)  # First step has additional 0.2 seconds to prevent race conditions
        self.assertEqual(core.mixer.set_volume.call_count, 2)
        core.mixer.set_volume.assert_called_with(100)
        self.assertEqual(threading.active_count(), threadcount)

        time.sleep(5)  # More than 3x increase step time
        self.assertEqual(core.mixer.set_volume.call_count, 2)
        core.mixer.set_volume.assert_called_with(100)
        self.assertEqual(threading.active_count(), threadcount)

    def test03_adjust_volume__100_0(self):
        core = mock.Mock()
        threadcount = threading.active_count()

        am = AlarmManager()
        am.get_core(core)

        self.assertEqual(threading.active_count(), threadcount)

        am.adjust_volume(100, 0, 0)

        core.mixer.set_volume.assert_called_once_with(100)
        self.assertEqual(threading.active_count(), threadcount)

        time.sleep(5)  # More than 3x increase step time
        core.mixer.set_volume.assert_called_once_with(100)
        self.assertEqual(threading.active_count(), threadcount)

    def test03_adjust_volume__3_17(self):
        core = mock.Mock()
        threadcount = threading.active_count()

        am = AlarmManager()
        am.get_core(core)

        self.assertEqual(threading.active_count(), threadcount)

        am.adjust_volume(3, 17, 0)

        core.mixer.set_volume.assert_called_once_with(1)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(5.87)  # First step has additional 0.2 seconds to prevent race conditions
        self.assertEqual(core.mixer.set_volume.call_count, 2)
        core.mixer.set_volume.assert_called_with(2)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(5.67)
        self.assertEqual(core.mixer.set_volume.call_count, 3)
        core.mixer.set_volume.assert_called_with(2)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(5.67)
        self.assertEqual(core.mixer.set_volume.call_count, 4)
        core.mixer.set_volume.assert_called_with(3)
        self.assertEqual(threading.active_count(), threadcount)

        time.sleep(20)  # More than 3x increase step time
        self.assertEqual(core.mixer.set_volume.call_count, 4)
        core.mixer.set_volume.assert_called_with(3)
        self.assertEqual(threading.active_count(), threadcount)

    def test03_adjust_volume__80_10(self):
        core = mock.Mock()
        threadcount = threading.active_count()

        am = AlarmManager()
        am.get_core(core)

        self.assertEqual(threading.active_count(), threadcount)

        am.adjust_volume(80, 10, 0)

        core.mixer.set_volume.assert_called_once_with(7)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(1.2)  # First step has additional 0.2 seconds to prevent race conditions
        self.assertEqual(core.mixer.set_volume.call_count, 2)
        core.mixer.set_volume.assert_called_with(15)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 3)
        core.mixer.set_volume.assert_called_with(22)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 4)
        core.mixer.set_volume.assert_called_with(29)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 5)
        core.mixer.set_volume.assert_called_with(36)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 6)
        core.mixer.set_volume.assert_called_with(44)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 7)
        core.mixer.set_volume.assert_called_with(51)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 8)
        core.mixer.set_volume.assert_called_with(58)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 9)
        core.mixer.set_volume.assert_called_with(65)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 10)
        core.mixer.set_volume.assert_called_with(73)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 11)
        core.mixer.set_volume.assert_called_with(80)
        self.assertEqual(threading.active_count(), threadcount)

        time.sleep(5)  # More than 3x increase step time
        self.assertEqual(core.mixer.set_volume.call_count, 11)
        core.mixer.set_volume.assert_called_with(80)
        self.assertEqual(threading.active_count(), threadcount)

    def test03_adjust_volume__100_30(self):
        core = mock.Mock()
        threadcount = threading.active_count()

        am = AlarmManager()
        am.get_core(core)

        self.assertEqual(threading.active_count(), threadcount)

        am.adjust_volume(100, 30, 0)

        core.mixer.set_volume.assert_called_once_with(3)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(1.2)  # First step has additional 0.2 seconds to prevent race conditions
        self.assertEqual(core.mixer.set_volume.call_count, 2)
        core.mixer.set_volume.assert_called_with(6)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 3)
        core.mixer.set_volume.assert_called_with(10)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 4)
        core.mixer.set_volume.assert_called_with(13)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 5)
        core.mixer.set_volume.assert_called_with(16)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 6)
        core.mixer.set_volume.assert_called_with(19)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 7)
        core.mixer.set_volume.assert_called_with(23)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 8)
        core.mixer.set_volume.assert_called_with(26)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 9)
        core.mixer.set_volume.assert_called_with(29)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 10)
        core.mixer.set_volume.assert_called_with(32)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 11)
        core.mixer.set_volume.assert_called_with(35)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 12)
        core.mixer.set_volume.assert_called_with(39)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 13)
        core.mixer.set_volume.assert_called_with(42)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 14)
        core.mixer.set_volume.assert_called_with(45)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 15)
        core.mixer.set_volume.assert_called_with(48)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 16)
        core.mixer.set_volume.assert_called_with(52)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 17)
        core.mixer.set_volume.assert_called_with(55)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 18)
        core.mixer.set_volume.assert_called_with(58)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 19)
        core.mixer.set_volume.assert_called_with(61)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 20)
        core.mixer.set_volume.assert_called_with(65)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 21)
        core.mixer.set_volume.assert_called_with(68)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 22)
        core.mixer.set_volume.assert_called_with(71)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 23)
        core.mixer.set_volume.assert_called_with(74)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 24)
        core.mixer.set_volume.assert_called_with(77)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 25)
        core.mixer.set_volume.assert_called_with(81)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 26)
        core.mixer.set_volume.assert_called_with(84)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 27)
        core.mixer.set_volume.assert_called_with(87)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 28)
        core.mixer.set_volume.assert_called_with(90)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 29)
        core.mixer.set_volume.assert_called_with(94)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 30)
        core.mixer.set_volume.assert_called_with(97)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 31)
        core.mixer.set_volume.assert_called_with(100)
        self.assertEqual(threading.active_count(), threadcount)

        time.sleep(5)  # More than 3x increase step time
        self.assertEqual(core.mixer.set_volume.call_count, 31)
        core.mixer.set_volume.assert_called_with(100)
        self.assertEqual(threading.active_count(), threadcount)

    def test03_adjust_volume__100_30_intervened(self):
        core = mock.Mock()
        threadcount = threading.active_count()

        am = AlarmManager()
        am.get_core(core)

        self.assertEqual(threading.active_count(), threadcount)

        am.adjust_volume(100, 30, 0)

        core.mixer.set_volume.assert_called_once_with(3)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(1.2)  # First step has additional 0.2 seconds to prevent race conditions
        self.assertEqual(core.mixer.set_volume.call_count, 2)
        core.mixer.set_volume.assert_called_with(6)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 3)
        core.mixer.set_volume.assert_called_with(10)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 4)
        core.mixer.set_volume.assert_called_with(13)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 5)
        core.mixer.set_volume.assert_called_with(16)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 6)
        core.mixer.set_volume.assert_called_with(19)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 7)
        core.mixer.set_volume.assert_called_with(23)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 8)
        core.mixer.set_volume.assert_called_with(26)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 9)
        core.mixer.set_volume.assert_called_with(29)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 10)
        core.mixer.set_volume.assert_called_with(32)
        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 11)
        core.mixer.set_volume.assert_called_with(35)
        self.assertEqual(threading.active_count(), threadcount + 1)

        core.mixer.set_volume(14)
        core.mixer.get_volume().get.side_effect = lambda: 14  # Intervention: set volume to 14
        self.assertEqual(threading.active_count(), threadcount + 1)

        time.sleep(1)
        self.assertEqual(core.mixer.set_volume.call_count, 12)
        core.mixer.set_volume.assert_called_with(14)
        self.assertEqual(threading.active_count(), threadcount)

        time.sleep(5)  # More than 3x increase step time
        self.assertEqual(core.mixer.set_volume.call_count, 12)
        core.mixer.set_volume.assert_called_with(14)
        self.assertEqual(threading.active_count(), threadcount)

    def test04__integration_1(self):
        core = mock.Mock()
        playlist = 'Playlist URI'
        core.playback.get_state().get.side_effect = lambda: PlaybackState.PLAYING
        core.playback.get_time_position().get.side_effect = lambda: 234
        core.playlists.lookup('Playlist URI').get().tracks = 'Tracks 811, 821, 823, 827, 829, 839'
        core.tracklist.get_length().get.side_effect = lambda: 4
        self.assertEqual(core.playlists.lookup.call_count, 1)  # First call when setting up the Mock
        threadcount = threading.active_count()

        am = AlarmManager()

        # Test get_core()
        self.assertTrue(am is am.get_core(core))

        # Test is_set() and threading when NOT set
        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

        # Set alarm to FAR future
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        # Test when set
        self.assertTrue(am.is_set())
        self.assertEqual(threading.active_count(), threadcount + 1)
        self.assertEqual(am.get_ring_time(), '07:59')
        self.assertFalse(am.random_mode)
        self.assertEqual(am.volume, 41)
        self.assertEqual(am.volume_increase_seconds, 83)

        # Cancel alarm
        am.cancel()

        # Test is_set() and threading when NOT set
        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

        # Set alarm to NEAR future
        am.set_alarm(datetime.datetime.now() + datetime.timedelta(seconds=29), playlist, False, 23, 127)

        # Tests a few seconds BEFORE alarm
        time.sleep(27)
        self.assertTrue(am.is_set())
        self.assertEqual(threading.active_count(), threadcount + 1)
        self.assertFalse(am.random_mode)
        self.assertEqual(am.volume, 23)
        self.assertEqual(am.volume_increase_seconds, 127)
        self.assertEqual(core.playlists.lookup.call_count, 1)  # First call when setting up the Mock

        # Cancel alarm
        am.cancel()

        # Test is_set() and threading when NOT set
        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

        # Sleep 20 seconds more to ensure that alarm will start if not cancelled
        time.sleep(20)

        # Set alarm to NEAR future
        am.set_alarm(datetime.datetime.now() + datetime.timedelta(seconds=31), playlist, True, 3, 17)

        # Test when set
        self.assertTrue(am.is_set())
        self.assertEqual(threading.active_count(), threadcount + 1)
        self.assertTrue(am.random_mode)
        self.assertEqual(am.volume, 3)
        self.assertEqual(am.volume_increase_seconds, 17)

        # Tests a few seconds BEFORE alarm
        time.sleep(29)
        self.assertTrue(am.is_set())
        self.assertEqual(threading.active_count(), threadcount + 1)
        self.assertEqual(core.tracklist.set_consume.call_count, 0)
        self.assertEqual(core.tracklist.set_single.call_count, 0)
        self.assertEqual(core.tracklist.set_repeat.call_count, 0)
        self.assertEqual(core.tracklist.set_random.call_count, 0)
        self.assertEqual(core.mixer.set_mute.call_count, 0)
        self.assertEqual(core.mixer.set_volume.call_count, 0)
        self.assertEqual(core.playback.stop.call_count, 0)
        self.assertEqual(core.tracklist.clear.call_count, 0)
        self.assertEqual(core.tracklist.add.call_count, 0)
        self.assertEqual(core.playback.next.call_count, 0)
        self.assertEqual(core.playback.play.call_count, 0)
        self.assertEqual(core.playlists.lookup.call_count, 1)  # First call when setting up the Mock

        # Tests a few seconds AFTER alarm START
        time.sleep(8)
        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount + 1)  # Additional thread is created by adjust_volume()

        core.tracklist.set_consume.assert_called_once_with(False)
        core.tracklist.set_single.assert_called_once_with(False)
        core.tracklist.set_repeat.assert_called_once_with(True)
        core.tracklist.set_random.assert_called_once_with(True)
        core.mixer.set_mute.assert_called_once_with(False)
        self.assertEqual(core.mixer.set_volume.call_count, 2)
        core.mixer.set_volume.assert_called_with(1)  # First step of gradual volume increasing

        core.playback.stop.assert_called_once_with()
        core.tracklist.clear.assert_called_once_with()
        core.tracklist.add.assert_called_once_with('Tracks 811, 821, 823, 827, 829, 839')
        core.playback.next.assert_called_once_with()
        core.playback.play.assert_called_once_with()
        self.assertEqual(core.playlists.lookup.call_count, 2)

        # Further tests of gradual volume increasing
        time.sleep(5.67)  # Race conditions already prevented by previous sleep()
        self.assertEqual(core.mixer.set_volume.call_count, 3)
        core.mixer.set_volume.assert_called_with(2)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(5.67)
        self.assertEqual(core.mixer.set_volume.call_count, 4)
        core.mixer.set_volume.assert_called_with(2)
        self.assertEqual(threading.active_count(), threadcount + 1)
        time.sleep(5.67)
        self.assertEqual(core.mixer.set_volume.call_count, 5)
        core.mixer.set_volume.assert_called_with(3)
        self.assertEqual(threading.active_count(), threadcount)
        time.sleep(20)  # More than 3x increase step time
        self.assertEqual(core.mixer.set_volume.call_count, 5)
        core.mixer.set_volume.assert_called_with(3)
        self.assertEqual(threading.active_count(), threadcount)

        # Test alarm cancellation after alarm has been started
        self.assertFalse(am.is_set())
        am.cancel()
        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

        # Set alarm to FAR future
        am.set_alarm(datetime.datetime(2055, 4, 28, 7, 59, 15, 324341), playlist, False, 41, 83)

        # Test when set
        self.assertTrue(am.is_set())
        self.assertEqual(threading.active_count(), threadcount + 1)
        self.assertEqual(am.get_ring_time(), '07:59')
        self.assertFalse(am.random_mode)
        self.assertEqual(am.volume, 41)
        self.assertEqual(am.volume_increase_seconds, 83)

        # Cancel alarm
        am.cancel()

        # Test is_set() and threading when NOT set
        self.assertFalse(am.is_set())
        self.assertEqual(threading.active_count(), threadcount)

    # TODO Write more (granular + comprehensive) tests
