from __future__ import unicode_literals

import datetime
import os
import re

import tornado.template
import tornado.web

from alarm_manager import parse_time


template_directory = os.path.join(os.path.dirname(__file__), 'templates')
template_loader = tornado.template.Loader(template_directory)

MESSAGES = {
    'ok': (u'Alarm has been properly set.', 'success'),
    'format': (u'The date\'s format you specified is incorrect.', 'danger'),
    'cancel': (u'Alarm has been canceled.', 'success'),
    'bad': (u'The request was invalid.', 'danger'),
}


class BaseRequestHandler(tornado.web.RequestHandler):
    def initialize(self, config, core, alarm_manager, msg_store):
        self.config = config
        self.core = core
        self.alarm_manager = alarm_manager
        self.msg_store = msg_store

    def send_message(self, code):
        self.msg_store.msg_code = code
        self.redirect('/alarmclock/')


class MainRequestHandler(BaseRequestHandler):
    def get(self):
        message = None
        if self.msg_store.msg_code and self.msg_store.msg_code in MESSAGES:
            message = MESSAGES[self.msg_store.msg_code]
            self.msg_store.msg_code = None

        playlists = self.core.playlists.playlists.get()

        self.write(template_loader.load('index.html').generate(
            playlists=playlists,
            alarm_manager=self.alarm_manager,
            message=message,
            config=self.config['alarmclock']
        ))


class DeleteAlarmRequestHandler(BaseRequestHandler):
    def post(self):
        alarmidx = int(self.get_argument('alarm', -1))
        if not 0 <= alarmidx < len(self.alarm_manager.alarms):
            self.send_message('bad')
            return
        del self.alarm_manager.alarms[alarmidx]
        self.alarm_manager.save_alarms()
        self.send_message('cancel')


class NewAlarmRequestHandler(BaseRequestHandler):
    def post(self):
        self.alarm_manager.create_alarm()
        self.send_message('ok')


class SetAlarmRequestHandler(BaseRequestHandler):
    def post(self):
        # FIXME: Code duplication
        alarmidx = int(self.get_argument('alarm', -1))
        if not 0 <= alarmidx < len(self.alarm_manager.alarms):
            self.send_message('bad')
            return
        alarm = self.alarm_manager.alarms[alarmidx]

        enabled = bool(self.get_argument('enabled', False))
        playlist = self.get_argument('playlist', None)

        time = parse_time(self.get_argument('time', None))
        random_mode = bool(self.get_argument('random', False))

        # Get and sanitize volume and seconds to full volume
        volume = int(self.get_argument('volume', 100))
        volume = max(min(volume, 100), 1)

        volume_increase_seconds = int(self.get_argument('incsec', 30))
        volume_increase_seconds = max(min(volume_increase_seconds, 300), 0)

        if time is not None:
            alarm.alarm_time = time
            alarm.playlist = playlist
            alarm.random_mode = random_mode
            alarm.volume = volume
            alarm.volume_increase_seconds = volume_increase_seconds
            alarm.enabled = enabled
            self.alarm_manager.save_alarms()
            self.send_message('ok')
        else:
            self.send_message('format')


class MessageStore(object):
    msg_code = None  # Message to be stored


# little hack to pass a persistent instance (alarm_manager) to the handler
# and pass the instance of mopidy.Core to the AlarmManager (via get_core)
def factory_decorator(alarm_manager, msg_store):
    def app_factory(config, core):
        # since all the RequestHandler-classes get the same arguments ...
        def bind(url, klass):
            return (url, klass, {'config': config, 'core': core, 'alarm_manager': alarm_manager.get_core(config, core), 'msg_store': msg_store})

        return [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static')}),

            bind('/', MainRequestHandler),
            bind('/delete/', DeleteAlarmRequestHandler),
            bind('/new/', NewAlarmRequestHandler),
            bind('/set/', SetAlarmRequestHandler),
        ]

    return app_factory
