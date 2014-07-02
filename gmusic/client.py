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

    def get_current_song(self):
        return DBSession.query(Song).filter(
            Song.id == self.current_song
        ).first()

    def get_current_time(self):
        ctime = self.position
        if self.status == "playing":
            ctime = time.time() - self.start_time
        if ctime > self.duration:
            self._queue.pop(0)
            self.current_song = self._queue[0]
            ctime = 0
        return ctime

    def play(self):
        if len(self._queue) <= 0:
            self.status = "stopped"
            return
        if not self.current_song:
            self.current_song = self._queue[0]
        if self.status is not "playing":
            self.status = "playing"
            self.start_time = time.time()

    def pause(self):
        if self.status is "playing":
            self.status = "paused"
            self.position = self.get_current_time()

    def next_song(self):
        self.status = "stopped"
        if len(self._queue) <= 0:
            return
        self.position = 0
        self._queue.pop(0)
        self.current_song = self._queue[0]
        self.start_time = time.time()
        self.play()

    def add_to_queue(self, song_id):
        self._queue.append(song_id)

    def remove_from_queue(self, position):
        del self._queue[position]

    def play_next_in_queue(self, song_id):
        self._queue.insert(1, song_id)

    def play_now_in_queue(self, song_id):
        self._queue.insert(1, song_id)
        if len(self._queue) > 1:
            self.remove_from_queue(0)

    @property
    def duration(self):
        song = self.get_current_song()
        if song:
            return song.duration
        return 0

    @property
    def queue(self):
        self.play()
        return self._queue
