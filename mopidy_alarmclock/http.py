from __future__ import unicode_literals

import os

import tornado.web, tornado.template

from mopidy import ext

import logging, time
from datetime import datetime
from threading import Timer

logging.getLogger(__name__)

template_directory = os.path.join(os.path.dirname(__file__), 'templates')
template_loader = tornado.template.Loader(template_directory)

MESSAGES = {
    'ok':'Alarm has been properly set.',
    'past':'The date you specified is in the past.',
    'format':'The date\'s format you specified is incorrect.',
    'cancel':'Alarm has been canceled.',
}

#Enum of states
class states:
    DISABLED = 1
    WAITING = 2
    CANCELED = 3

class AlarmManager(object):
    clock_datetime = None #datetime of when the alarm clock begins to play music
    playlist = None #playlist to play
    shuffle_mode = False #True if the playlist will be played in shuffle mode
    core = None
    state = states.DISABLED

    def is_set(self):
        return (self.state == states.WAITING)

    def reset(self):
        self.clock_datetime = None
        self.playlist = None
        self.shuffle_mode = False

    def cancel(self):
        self.reset()
        self.state = states.CANCELED

    def set_alarm(self, core, clock_datetime, playlist, mode):
        self.core = core
        self.clock_datetime = clock_datetime
        self.playlist = playlist
        self.shuffle_mode = mode
        self.state = states.WAITING

        self.idle()

    def play(self):
        self.core.playback.stop()
        self.core.tracklist.clear()
        self.core.tracklist.add(self.playlist.tracks)
        if self.shuffle_mode:
            self.core.tracklist.shuffle()

        self.core.playback.play()

        self.reset()
        self.state = states.DISABLED

    def idle(self):
        if self.state == states.WAITING: #alarm can be canceled, check if not
            if datetime.now() > self.clock_datetime: #time to make some noise
                self.play()
            else:
                t = Timer(60, self.idle) #check each minute if the clock must start or not
                t.start()

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
        datetime_string = self.get_argument('datetime', None)
        try:
            date = datetime.fromtimestamp(time.mktime(time.strptime(datetime_string, '%d/%m/%Y %H:%M')))
        except ValueError: #incorrect date format
            date = None
        if not date:
            self.send_message('format')
        elif date <= datetime.today():
            self.send_message('past')
        else:
            self.alarm_manager.set_alarm(self.core, date, playlist, False) #TODO False mode shuffle
            self.send_message('ok')

class CancelAlarmRequestHandler(BaseRequestHandler):
    def get(self):
        self.alarm_manager.cancel()
        self.send_message('cancel')

#little hack to pass a persistent instance (alarm_manager) to the handler
def factory_decorator(alarm_manager):
    def app_factory(config, core):
        #since all of mine RequestHandler-classes get the same arguments ...
        bind = lambda url, klass : (url, klass, {'core': core, 'alarm_manager':alarm_manager})

        return [
            bind('/', MainRequestHandler),
            bind('/set/', SetAlarmRequestHandler),
            bind('/cancel/', CancelAlarmRequestHandler),
        ]

    return app_factory
