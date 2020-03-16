import datetime
import logging
import os
import time
from threading import Timer

import monotonic

from mopidy.core import PlaybackState


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
    logger = logging.getLogger(__name__)

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

    def play(self, fallback=False):
        self.logger.info("AlarmClock alarm started (fallback %s)", fallback)
        self.core.playback.stop()
        self.core.tracklist.clear()

        try:
            if fallback:
                raise Exception('Fallback')
            self.core.tracklist.add(self.get_playlist().tracks)
            if self.core.tracklist.get_length().get() < 1:
                raise Exception('Tracklist empty')
        except Exception as e:
            self.logger.info("AlarmClock using backup alarm, reason: %s", e)
            self.core.tracklist.add(None, 0, ['file://' + os.path.join(os.path.dirname(__file__), 'backup-alarm.mp3')])

        self.core.tracklist.set_consume(False)
        self.core.tracklist.set_single(False)
        self.core.tracklist.set_repeat(True)

        self.core.tracklist.set_random(self.random_mode)
        if self.random_mode:
            self.core.playback.next()

        self.core.mixer.set_mute(False)
        self.core.mixer.set_volume(0)

        self.core.playback.play()

        if not fallback:  # do fallback only once
            self.logger.info("AlarmClock waiting for playback to start")
            waited = 0.5
            starttime = 0
            try:
                starttime = monotonic.monotonic()
                time.sleep(0.5)
                while self.core.playback.get_state().get() != PlaybackState.PLAYING or self.core.playback.get_time_position().get() < 100:  # in some cases this check will cause a notable delay
                    self.logger.info("AlarmClock has been waiting for %.2f seconds (waited inside AlarmClock %.2f sec)", monotonic.monotonic() - starttime, waited)
                    if waited > 30 or (waited > 0.5 and monotonic.monotonic() - starttime > 30):  # ensure EITHER delay is more than 30 seconds OR at least 2 times above line has been executed
                        raise Exception("Timeout")
                    time.sleep(1)
                    waited += 1
                self.logger.info("AlarmClock playback started within %.2f seconds (waited inside AlarmClock %.2f sec)", monotonic.monotonic() - starttime, waited)
            except Exception as e:
                self.logger.info("AlarmClock playback FAILED to start (waited inside AlarmClock %.2f sec), reason: %s", waited, e)
                self.play(True)
                return

        self.adjust_volume(self.volume, self.volume_increase_seconds, 0)

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
            current_volume = self.core.mixer.get_volume().get()
        except Exception:
            pass
        if step_no == 0 or not isinstance(current_volume, int) or current_volume == int(round(target_volume * (step_no) / (number_of_steps + 1))):
            if step_no >= number_of_steps:  # this design should prevent floating-point edge-case bugs (in case such bugs could be possible here)
                self.logger.info("AlarmClock increasing volume to target volume %d", target_volume)
                self.core.mixer.set_volume(target_volume)
            else:
                self.logger.info("AlarmClock increasing volume to %d", int(round(target_volume * (step_no + 1) / (number_of_steps + 1))))
                self.core.mixer.set_volume(int(round(target_volume * (step_no + 1) / (number_of_steps + 1))))
                t = Timer(increase_duration / number_of_steps, self.adjust_volume, [target_volume, increase_duration, step_no + 1])
                t.start()
