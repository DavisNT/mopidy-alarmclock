from __future__ import division
from __future__ import unicode_literals

import collections
import datetime
import json
import logging
import os
from threading import Timer



logger = logging.getLogger(__name__)


class Alarm(object):
    alarm_time = None  # datetime of when the alarm clock begins to play music
    playlist = None  # URI of playlist to play
    random_mode = None  # True if the playlist will be played in shuffle mode
    volume = None  # Alarm volume
    volume_increase_seconds = None  # Seconds to full volume
    enabled = False
    days = None

    def __init__(self):
        self.alarm_time = datetime.time()
        self.days = [ 0, 1, 2, 3, 4, 5, 6 ] # Weekdays the alarm will fire

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
    def set_for_today(self):
        '''
        Returns whether the alarm is set to go off on this day of the week.
        '''
        today = datetime.datetime.now().weekday()
        return today in self.days

    @property
    def formatted_ring_time(self):
        return self.alarm_time.strftime('%H:%M')

    def __str__(self):
        # TODO: Make this more useful
        return self.formatted_ring_time + ' alarm'


class AlarmEncoder(json.JSONEncoder):
    def default(self, o):
        if not isinstance(o, Alarm):
            return super(AlarmEncoder, self).default(self, o)

        return collections.OrderedDict([
            ('time', o.alarm_time.strftime('%H:%M')),
            ('playlist', o.playlist),
            ('enabled', o.enabled),
            ('random', o.random_mode),
            ('volume', o.volume),
            ('volume_increase_seconds', o.volume_increase_seconds),
            ('days', o.days),
        ])


def alarm_decoder(o):
    if 'time' not in o:
        return o

    a = Alarm()
    a.alarm_time = datetime.datetime.strptime(o['time'], '%H:%M').time()
    a.playlist = o['playlist']
    a.enabled = o.get('enabled', True)
    a.random_mode = o.get('random', False)
    a.volume = o.get('volume', 100)
    a.volume_increase_seconds = o.get('volume_increase_seconds', 0)
    a.days = o.get('days', a.days)
    return a


class AlarmManager(object):
    ext = None
    core = None
    config = None
    alarms = None
    last_fired = None

    def __init__(self, ext):
        self.alarms = []
        self.ext = ext

        # Start the timer
        self.last_fired = datetime.datetime.now()
        self.idle()

    def load_alarms(self):
        logger.info('Reading alarm configuration')
        try:
            dir = self.ext.get_data_dir(self.config)
            with open(os.path.join(dir, 'alarms.json')) as fp:
                self.alarms = json.load(fp, object_hook=alarm_decoder)
        except:
            logger.exception('Could not load saved alarms')

    def save_alarms(self):
        logger.info('Writing out alarm configuration')
        try:
            dir = self.ext.get_data_dir(self.config)
            with open(os.path.join(dir, 'alarms.json'), 'w') as fp:
                json.dump(self.alarms, fp, cls=AlarmEncoder, indent=2)
        except:
            logger.exception('Could not save alarms')

    def create_alarm(self):
        # TODO: Fill out defaults from config file
        self.alarms.append(Alarm())
        self.save_alarms()

    def get_core(self, config, core):
        if self.core is None:
            # First time loading
            self.config = config
            self.core = core
            self.load_alarms()
        return self

    def get_seconds_since_midnight(self):
        # snippet found here http://stackoverflow.com/a/15971505/927592
        now = datetime.datetime.now()
        return int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())

    def play(self, alarm):
        self.core.playback.stop()
        self.core.tracklist.clear()

        try:
            playlist = self.core.playlists.lookup(alarm.playlist).get()
            self.core.tracklist.add(playlist.tracks)
            if self.core.tracklist.length.get() < 1:
                raise Exception('Tracklist empty')
        except:
            # TODO: This should be optional
            logger.exception('Failed to load playlist, playing backup alarm')
            self.core.tracklist.add(None, 0, 'file://' + os.path.join(os.path.dirname(__file__), 'backup-alarm.mp3'))

        self.core.tracklist.consume = False
        self.core.tracklist.single = False
        self.core.tracklist.repeat = True

        self.core.tracklist.random = alarm.random_mode
        if self.core.tracklist.random:
            self.core.playback.next()

        self.core.playback.mute = False

        self.adjust_volume(alarm.volume, alarm.volume_increase_seconds)

        self.core.playback.play()

    def idle(self):
        logger.debug('Alarm check timer is now firing')
        now = datetime.datetime.now()

        # TODO: Disable the timer if none of our alarms are enabled
        for alarm in self.alarms:
            if alarm.enabled and alarm.set_for_today and self.last_fired < alarm.datetime_today <= now:
                logger.info('Triggering alarm {}'.format(alarm))
                self.play(alarm)
                break  # Assume that multiple alarms don't fire

        # Rinse, repeat
        self.last_fired = now
        Timer(5, self.idle).start()

    def adjust_volume(self, target_volume, increase_duration):
        '''
        Scales the current volume up to or down to the target volume over a
        few seconds.
        '''

        try:
            current_volume = self.core.playback.volume.get()
        except:
            logger.exception('Could not get current playback volume')
            self.core.playback.volume = target_volume
            return

        if target_volume == current_volume:
            logger.debug('Volume is already the desired level')
            return

        if increase_duration == 0:
            logger.debug('Setting volume without scaling')
            self.core.playback.volume = target_volume
            return

        # This is when we will finish fading
        fade_start = datetime.datetime.now()
        fade_end = fade_start + datetime.timedelta(seconds=increase_duration)
        logger.debug('Scaling volume from {} to {} from now until {}'.format(current_volume, target_volume, fade_end))

        # Compute the time to increase the volume by 1
        period = float(increase_duration) / abs(target_volume - current_volume)
        direction = cmp(target_volume, current_volume)

        def step():
            now = datetime.datetime.now()
            if now >= fade_end:
                logger.debug('Fade deadline has passed, setting volume')
                self.core.playback.volume = target_volume
                return

            # We don't know that we fired at the right time, so we can't
            # just increment current_volume. Calculate where we should be.
            new_volume = current_volume + direction * int((now - fade_start).total_seconds() / period)
            logger.debug('Stepping volume to {}, target volume is {}'.format(new_volume, target_volume))
            self.core.playback.volume = new_volume

            Timer(period, step).start()
        step()
