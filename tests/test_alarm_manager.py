from __future__ import unicode_literals

import unittest

import mock

from alarm_manager import AlarmManager


class AlarmManagerTest(unittest.TestCase):

    def test_get_seconds_since_midnight(self):
        am = AlarmManager()

        seconds = am.get_seconds_since_midnight()
        
        self.assertIsInstance(seconds, int)
        self.assertTrue(seconds >= 0 and seconds < 86400)
