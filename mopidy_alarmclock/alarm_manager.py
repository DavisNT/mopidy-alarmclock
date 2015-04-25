from __future__ import unicode_literals
import datetime
from threading import Timer

#Enum of states
class states:
    DISABLED = 1
    WAITING = 2
    CANCELED = 3

class AlarmManager(object):
    clock_datetime = None #datetime of when the alarm clock begins to play music
    playlist = None #playlist to play
    random_mode = None #True if the playlist will be played in shuffle mode
    volume = None #Alarm volume
    volume_increase_seconds = None #Seconds to full volume
    core = None
    state = states.DISABLED

    def get_core(self, core):
        self.core = core
        return self

    def is_set(self):
        return (self.state == states.WAITING)

    def get_ring_time(self):
        return self.clock_datetime.strftime('%H:%M')

    def reset(self):
        self.clock_datetime = None
        self.playlist = None
        self.random_mode = None
        self.volume = None
        self.volume_increase_seconds = None

    def cancel(self):
        self.reset()
        self.state = states.CANCELED

    def set_alarm(self, clock_datetime, playlist, random_mode, volume, volume_increase_seconds):
        self.clock_datetime = clock_datetime
        self.playlist = playlist
        self.random_mode = random_mode
        self.volume = volume
        self.volume_increase_seconds = volume_increase_seconds
        self.state = states.WAITING

        self.idle()

    def play(self):
        self.core.playback.stop()
        self.core.tracklist.clear()
        self.core.tracklist.add(self.playlist.tracks)

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
        if self.state == states.WAITING: #alarm can be canceled, check if not
            if datetime.datetime.now() >= self.clock_datetime: #time to make some noise
                self.play()
            else:
                t = Timer(5, self.idle) #check each 5 seconds if the alarm must start or not
                t.start()

    def adjust_volume(self, target_volume, increase_duration, step_no):
        number_of_steps = min(target_volume, increase_duration)
        current_volume = self.core.playback.volume
        if callable(getattr(current_volume, 'get', None)): #workaround for Mopidy 1.0
            current_volume = current_volume.get()
        if step_no == 0 or not isinstance(current_volume, int) or current_volume == int(round(target_volume * (step_no) / (number_of_steps + 1))):
            if step_no >= number_of_steps: #this design should prevent floating-point edge-case bugs (in case such bugs could be possible here)
                self.core.playback.volume = target_volume
            else:
                self.core.playback.volume = int(round(target_volume * (step_no + 1) / (number_of_steps + 1)))
                t = Timer(increase_duration / number_of_steps, self.adjust_volume, [target_volume, increase_duration, step_no + 1])
                t.start()

