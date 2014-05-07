import threading
import time

from .models import (
    DBSession,
    Song,
)


class MusicClient():

    def __init__(self):
        self.status = "stopped"
        self.current_song = None
        self.start_time = 0
        self.position = 0
        self._queue = []
        self._timer = None

    def get_current_song(self):
        return DBSession.query(Song).filter(
            Song.id == self.current_song
        ).first()

    def get_current_time(self):
        return time.time() - self.start_time

    def play(self):
        if len(self._queue) <= 0:
            return
        if not self.current_song:
            self.current_song = self._queue[0]
        if self.status is not "playing":
            self.status = "playing"
            self.start_time = time.time()
            self._timer = threading.Timer(
                self.get_current_song().duration - self.position,
                self.next_song
            )
            self._timer.start()
            print "=============="
            print self.get_current_song().duration - self.position
            print "=============="

    def pause(self):
        if self.status is "playing":
            self.status = "paused"
            self._timer.cancel()
            self.position = self.get_current_time()

    def next_song(self):
        if len(self._queue) <= 0:
            self.status = "stopped"
            return
        self.position = 0
        self.current_song = self._queue.pop(0)
        self.start_time = time.time()
        self.play()

    def add_to_queue(self, song_id):
        self._queue.append(song_id)

    def remove_from_queue(self, position):
        self._queue[position]

    def play_next_in_queue(self, song_id):
        self._queue.insert(1, song_id)

    def play_now_in_queue(self, song_id):
        self._queue.insert(1, song_id)
        if len(self._queue) > 1:
            self.remove_from_queue(0)

    @property
    def queue(self):
        self.play()
        print self.status, self.get_current_time()
        return self._queue
