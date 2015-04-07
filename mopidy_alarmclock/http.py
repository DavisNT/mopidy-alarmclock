from __future__ import unicode_literals

import tornado.web, tornado.template

import logging, time, datetime, os, re

#logging.getLogger(__name__)

template_directory = os.path.join(os.path.dirname(__file__), 'templates')
template_loader = tornado.template.Loader(template_directory)

MESSAGES = {
    'ok': (u'Alarm has been properly set.','success'),
    'format': (u'The date\'s format you specified is incorrect.','danger'),
    'cancel': (u'Alarm has been canceled.','success'),
}

class BaseRequestHandler(tornado.web.RequestHandler):
    def initialize(self, core, alarm_manager):
        self.core = core
        self.alarm_manager = alarm_manager

    def send_message(self, code):
        self.redirect('/alarmclock/?msg=%s' % code)

class MainRequestHandler(BaseRequestHandler):
    def get(self):
        message = None
        msg_code = self.get_argument('msg',None)
        if msg_code and msg_code in MESSAGES:
            message = MESSAGES[msg_code]

        playlists = self.core.playlists.playlists.get()

        self.write(template_loader.load('index.html').generate(
            playlists=playlists,
            alarm_manager=self.alarm_manager,
            message=message,
        ))

class SetAlarmRequestHandler(BaseRequestHandler):
    def post(self):
        playlist = self.get_argument('playlist',None)
        playlist = self.core.playlists.lookup(playlist).get()

        time_string = self.get_argument('time', None)
        #RE found here http://stackoverflow.com/questions/7536755/regular-expression-for-matching-hhmm-time-format
        matched = re.match('^([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$', time_string)
        random_mode = bool(self.get_argument('random', False))

        if matched:
            time_comp = map(lambda x: int(x), matched.groups())
            time = datetime.time(hour=time_comp[0], minute=time_comp[1])

            dt = datetime.datetime.combine(datetime.datetime.now(), time)
            if datetime.datetime.now() >= dt:
                dt += datetime.timedelta(days=1)

            self.alarm_manager.set_alarm(dt, playlist, random_mode)
            self.send_message('ok')
        else:
            self.send_message('format')

class CancelAlarmRequestHandler(BaseRequestHandler):
    def get(self):
        self.alarm_manager.cancel()
        self.send_message('cancel')

#little hack to pass a persistent instance (alarm_manager) to the handler
#and pass the instance of mopidy.Core to the AlarmManager (via get_core)
def factory_decorator(alarm_manager):
    def app_factory(config, core):
        #since all the RequestHandler-classes get the same arguments ...
        bind = lambda url, klass : (url, klass, {'core': core, 'alarm_manager':alarm_manager.get_core(core)})

        return [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static')}),

            bind('/', MainRequestHandler),
            bind('/set/', SetAlarmRequestHandler),
            bind('/cancel/', CancelAlarmRequestHandler),
        ]

    return app_factory
