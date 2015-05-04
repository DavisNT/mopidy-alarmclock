from __future__ import unicode_literals

import unittest

import mock

from mopidy_alarmclock import Extension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn('[alarmclock]', config)
        self.assertIn('enabled = true', config)

        # WARNING! Default configuration must be also updated in README.rst and ext.conf
        # WARNING! Internal defaults of volume and volume increase seconds are in SetAlarmRequestHandler of http.py
        self.assertIn('def_time = 8:00', config)
        self.assertIn('def_playlist = ', config)
        self.assertIn('def_random = false', config)
        self.assertIn('def_volume = 100', config)
        self.assertIn('def_vol_inc_duration = 30', config)

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        # WARNING! Configuration element types not tested
        self.assertIn('def_time', schema)
        self.assertIn('def_playlist', schema)
        self.assertIn('def_random', schema)
        self.assertIn('def_volume', schema)
        self.assertIn('def_vol_inc_duration', schema)

    def test_setup(self):
        registry = mock.Mock()

        ext = Extension()
        ext.setup(registry)

        registry.add.assert_called_once_with('http:app', {
            'name': 'alarmclock',
            'factory': registry.add.call_args[0][1]['factory'],
        })
