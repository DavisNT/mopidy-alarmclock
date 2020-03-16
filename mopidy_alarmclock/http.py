import datetime
import os
import re

import tornado.template
import tornado.web


template_directory = os.path.join(os.path.dirname(__file__), 'templates')
template_loader = tornado.template.Loader(template_directory)

MESSAGES = {
    'ok': ('Alarm has been properly set.', 'success'),
    'format': ('The date\'s format you specified is incorrect.', 'danger'),
    'cancel': ('Alarm has been canceled.', 'success'),
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

        playlists = self.core.playlists.as_list().get()

        self.write(template_loader.load('index.html').generate(
            playlists=playlists,
            alarm_manager=self.alarm_manager,
            message=message,
            config=self.config['alarmclock']
        ))


class SetAlarmRequestHandler(BaseRequestHandler):
    def post(self):
        playlist = self.get_argument('playlist', None)

        time_string = self.get_argument('time', None)
        # Based on RE found here http://stackoverflow.com/a/7536768/927592
        matched = re.match('^([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-5]?[0-9])$', time_string)
        random_mode = bool(self.get_argument('random', False))

        # Get and sanitize volume and seconds to full volume
        volume = int(self.get_argument('volume', 100))
        volume_increase_seconds = int(self.get_argument('incsec', 30))
        if volume < 1 or volume > 100:
            volume = 100
        if volume_increase_seconds < 0 or volume_increase_seconds > 300:
            volume_increase_seconds = 30

        if matched:
            time_comp = [int(x) for x in matched.groups()]
            time = datetime.time(hour=time_comp[0], minute=time_comp[1])

            dt = datetime.datetime.combine(datetime.datetime.now(), time)
            if datetime.datetime.now() >= dt:
                dt += datetime.timedelta(days=1)

            self.alarm_manager.set_alarm(dt, playlist, random_mode, volume, volume_increase_seconds)
            self.send_message('ok')
        else:
            self.send_message('format')


class CancelAlarmRequestHandler(BaseRequestHandler):
    def get(self):
        self.alarm_manager.cancel()
        self.send_message('cancel')


class MessageStore(object):
    msg_code = None  # Message to be stored


# little hack to pass a persistent instance (alarm_manager) to the handler
# and pass the instance of mopidy.Core to the AlarmManager (via get_core)
def factory_decorator(alarm_manager, msg_store):
    def app_factory(config, core):
        # since all the RequestHandler-classes get the same arguments ...
        def bind(url, klass):
            return (url, klass, {'config': config, 'core': core, 'alarm_manager': alarm_manager.get_core(core), 'msg_store': msg_store})

        return [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static')}),

            bind('/', MainRequestHandler),
            bind('/set/', SetAlarmRequestHandler),
            bind('/cancel/', CancelAlarmRequestHandler),
        ]

    return app_factory
