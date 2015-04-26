from __future__ import unicode_literals

import unittest

from mopidy_alarmclock import Extension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn('[alarmclock]', config)
        self.assertIn('enabled = true', config)

    # TODO Write more tests
