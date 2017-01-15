from __future__ import division
from __future__ import unicode_literals

import datetime
import os
import time
from threading import Timer


# Enum of states
class states:
    DISABLED = 1
    WAITING = 2
    CANCELED = 3


class AlarmManager(object):
    clock_datetime = None  # datetime of when the alarm clock begins to play music
    playlist = None  # URI of playlist to play
    random_mode = None  # True if the playlist will be played in shuffle mode
    volume = None  # Alarm volume
    volume_increase_seconds = None  # Seconds to full volume
    core = None
    state = states.DISABLED
    idle_timer = None

    def get_core(self, core):
        self.core = core
        return self

    def is_set(self):
        return (self.state == states.WAITING)

    def get_ring_time(self):
        return self.clock_datetime.strftime('%H:%M')

    def get_playlist(self):
        return self.core.playlists.lookup(self.playlist).get()

    def get_seconds_since_midnight(self):
        # snippet found here http://stackoverflow.com/a/15971505/927592
        now = datetime.datetime.now()
        return int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())

    def reset(self):
        self.clock_datetime = None
        self.playlist = None
        self.random_mode = None
        self.volume = None
        self.volume_increase_seconds = None

    def cancel(self):
        self.reset()
        self.state = states.CANCELED
        if self.idle_timer is not None:
            while True:
                t = self.idle_timer
                t.cancel()
                if not t.is_alive():
                    if t is self.idle_timer:  # Ensure no new timer has been created
                        break
                time.sleep(0.05)

    def set_alarm(self, clock_datetime, playlist, random_mode, volume, volume_increase_seconds):
        self.clock_datetime = clock_datetime
        self.playlist = playlist
        self.random_mode = random_mode
        self.volume = volume
        self.volume_increase_seconds = volume_increase_seconds
        self.state = states.WAITING

        if self.idle_timer is not None:
            while True:
                t = self.idle_timer
                t.cancel()
                if not t.is_alive():
                    if t is self.idle_timer:  # Ensure no new timer has been created
                        break
                time.sleep(0.05)

        self.idle()

    def play(self):
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

        self.core.tracklist.random = self.random_mode
        if self.core.tracklist.random:
            self.core.playback.next()

        self.core.playback.mute = False

        self.adjust_volume(self.volume, self.volume_increase_seconds, 0)

        self.core.playback.play()

        self.reset()
        self.state = states.DISABLED

    def idle(self):
        if self.state == states.WAITING:  # alarm can be canceled, check if not
            if datetime.datetime.now() >= self.clock_datetime:  # time to make some noise
                self.play()
            else:
                t = Timer(5, self.idle)  # check each 5 seconds if the alarm must start or not
                t.start()
                self.idle_timer = t  # Atomically set idle_timer to next (alive!!!) timer

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
                t = Timer(increase_duration / number_of_steps, self.adjust_volume, [target_volume, increase_duration, step_no + 1])
                t.start()
