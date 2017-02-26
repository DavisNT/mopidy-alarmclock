from __future__ import division
from __future__ import unicode_literals

import datetime
import logging
import os
import time
from threading import Timer

logger = logging.getLogger(__name__)


class Alarm(object):
    alarm_time = None  # datetime of when the alarm clock begins to play music
    playlist = None  # URI of playlist to play
    random_mode = None  # True if the playlist will be played in shuffle mode
    volume = None  # Alarm volume
    volume_increase_seconds = None  # Seconds to full volume
    enabled = False

    def __init__(self):
        self.alarm_time = datetime.time()

    @property
    def datetime_today(self):
        '''
        Returns a datetime representing the time the alarm will go off today.
        '''
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        delta = datetime.timedelta(hours=self.alarm_time.hour, minutes=self.alarm_time.minute)
        return midnight + delta

    @property
    def formatted_ring_time(self):
        return self.alarm_time.strftime('%H:%M')

    def __str__(self):
        # TODO: Make this more useful
        return self.formatted_ring_time + ' alarm'


class AlarmManager(object):
    core = None
    alarms = None
    last_fired = None

    def __init__(self):
        self.alarms = [Alarm()]

        # Start the timer
        self.last_fired = datetime.datetime.now()
        self.idle()

    def create_alarm(self):
        # TODO: Fill out defaults from config file
        self.alarms.append(Alarm())

    def get_core(self, core):
        self.core = core
        return self

    def get_playlist(self):
        return self.core.playlists.lookup(self.alarms[0].playlist).get()

    def get_seconds_since_midnight(self):
        # snippet found here http://stackoverflow.com/a/15971505/927592
        now = datetime.datetime.now()
        return int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())

    def play(self, alarm):
        self.core.playback.stop()
        self.core.tracklist.clear()

        try:
            self.core.tracklist.add(self.get_playlist().tracks)
            if self.core.tracklist.length.get() < 1:
                raise Exception('Tracklist empty')
        except:
            self.core.tracklist.add(None, 0, 'file://' + os.path.join(os.path.dirname(__file__), 'backup-alarm.mp3'))

        self.core.tracklist.consume = False
        self.core.tracklist.single = False
        self.core.tracklist.repeat = True

        self.core.tracklist.random = alarm.random_mode
        if self.core.tracklist.random:
            self.core.playback.next()

        self.core.playback.mute = False

        self.adjust_volume(alarm.volume, alarm.volume_increase_seconds, 0)

        self.core.playback.play()

    def idle(self):
        logger.debug('Alarm check timer is now firing')
        now = datetime.datetime.now()

        # TODO: Disable the timer if none of our alarms are enabled
        for alarm in self.alarms:
            if alarm.enabled and self.last_fired < alarm.datetime_today <= now:
                logger.info('Triggering alarm {}'.format(alarm))
                self.play(alarm)
                break  # Assume that multiple alarms don't fire

        # Rinse, repeat
        self.last_fired = now
        Timer(5, self.idle).start()

    def adjust_volume(self, target_volume, increase_duration, step_no):
        number_of_steps = min(target_volume, increase_duration)
        current_volume = None
        try:
            current_volume = self.core.playback.volume.get()
        except:
            pass
        if step_no == 0 or not isinstance(current_volume, int) or current_volume == int(round(target_volume * (step_no) / (number_of_steps + 1))):
            if step_no >= number_of_steps:  # this design should prevent floating-point edge-case bugs (in case such bugs could be possible here)
                self.core.playback.volume = target_volume
            else:
                self.core.playback.volume = int(round(target_volume * (step_no + 1) / (number_of_steps + 1)))
                t = Timer(increase_duration / number_of_steps, self.alarms[0].adjust_volume, [target_volume, increase_duration, step_no + 1])
                t.start()
