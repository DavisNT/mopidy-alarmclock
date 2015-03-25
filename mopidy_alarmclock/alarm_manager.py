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
    shuffle_mode = False #True if the playlist will be played in shuffle mode
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
        self.shuffle_mode = False

    def cancel(self):
        self.reset()
        self.state = states.CANCELED

    def set_alarm(self, clock_datetime, playlist, mode):
        self.clock_datetime = clock_datetime
        self.playlist = playlist
        self.shuffle_mode = mode
        self.state = states.WAITING

        self.idle()

    def play(self):
        self.core.playback.stop()
        self.core.tracklist.clear()
        self.core.tracklist.add(self.playlist.tracks)

        self.core.tracklist.repeat = True

        self.core.tracklist.random = self.shuffle_mode
        if self.core.tracklist.random:
            self.core.playback.next()

        self.core.playback.mute = False
        self.core.playback.volume = 100

        self.core.playback.play()

        self.reset()
        self.state = states.DISABLED

    def idle(self):
        if self.state == states.WAITING: #alarm can be canceled, check if not
            if datetime.datetime.now() >= self.clock_datetime: #time to make some noise
                self.play()
            else:
                t = Timer(10, self.idle) #check each minute if the alarm must start or not
                t.start()


