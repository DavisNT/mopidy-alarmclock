from __future__ import unicode_literals

import unittest

from mopidy_alarmclock import Extension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn('[alarmclock]', config)
        self.assertIn('enabled = true', config)
        # WARNING! Default configuration must be also updated in README
        self.assertIn('def_time = 8:00', config)
        self.assertIn('def_playlist = ', config)
        self.assertIn('def_random = false', config)
        self.assertIn('def_volume = 100', config)
        self.assertIn('def_vol_inc_duration = 30', config)

    # TODO Write more tests
