from __future__ import unicode_literals

import os

from http import MessageStore, factory_decorator

from alarm_manager import AlarmManager

from mopidy import config, ext


__version__ = '0.1.6'


class Extension(ext.Extension):
    dist_name = 'Mopidy-AlarmClock'
    ext_name = 'alarmclock'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['def_time'] = config.String()
        schema['def_playlist'] = config.String(optional=True)
        schema['def_random'] = config.Boolean()
        schema['def_volume'] = config.Integer()
        schema['def_vol_inc_duration'] = config.Integer()
        return schema

    def setup(self, registry):
        alarm_manager = AlarmManager()
        msg_store = MessageStore()
        registry.add('http:app', {
            'name': self.ext_name,
            'factory': factory_decorator(alarm_manager, msg_store),
        })
