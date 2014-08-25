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

class AlarmManager(object):
    clock_datetime = None #datetime of when the alarm clock begins to play music
    playlist = None #playlist to play
    shuffle_mode = False #True if the playlist will be played in shuffle mode
    core = None

    def is_set(self):
        return self.clock_datetime

    def set_alarm(self, core, clock_datetime, playlist, mode):
        self.core = core
        self.clock_datetime = clock_datetime
        self.playlist = playlist
        self.shuffle_mode = mode

        self.idle()

    def play(self):
        self.core.playback.stop()
        self.core.tracklist.clear()
        self.core.tracklist.add(self.playlist.tracks)
        if self.shuffle_mode:
            self.core.tracklist.shuffle()

        self.core.playback.play()

        self.clock_datetime, self.playlist, self.shuffle_mode = None, None, None

    def idle(self):
        if self.clock_datetime and datetime.now() > self.clock_datetime:
            self.play()
        else:
            t = Timer(60, self.idle) #check each minute if the clock must ring or not
            t.start()

class MyRequestHandler(tornado.web.RequestHandler):
    def initialize(self, core, alarm_manager):
        self.core = core
        self.alarm_manager = alarm_manager

    def get(self):
        playlists = self.core.playlists.playlists.get()
        self.write(template_loader.load('index.html').generate(playlists=playlists, alarm_manager=self.alarm_manager))

    def post(self):
        playlist = self.get_argument('playlist',None)
        playlist = self.core.playlists.lookup(playlist).get()
        datetime_string = self.get_argument('datetime', None)
        date = datetime.fromtimestamp(time.mktime(time.strptime(datetime_string, '%d %m %Y %H:%M')))

        self.alarm_manager.set_alarm(self.core, date, playlist, False) #TODO False mode shuffle

        self.redirect('/alarmclock/')


def factory_decorator(alarm_manager):
    def app_factory(config, core):
        return [
            ('/', MyRequestHandler, {'core': core, 'alarm_manager':alarm_manager})
        ]

    return app_factory
