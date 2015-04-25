from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext

from http import factory_decorator, MessageStore
from alarm_manager import AlarmManager


__version__ = '0.1.3'

#logger = logging.getLogger(__name__)


class Extension(ext.Extension):
    dist_name = 'Mopidy-AlarmClock'
    ext_name = 'alarmclock'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        return schema

    def setup(self, registry):
        alarm_manager = AlarmManager()
        msg_store = MessageStore()
        registry.add('http:app', {
            'name': self.ext_name,
            'factory': factory_decorator(alarm_manager, msg_store),
        })
