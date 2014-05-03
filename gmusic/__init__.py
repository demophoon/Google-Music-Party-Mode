import sys
import logging
import time
import urllib
from tempfile import NamedTemporaryFile

import transaction
from pyramid.config import Configurator
from pyramid.response import FileResponse
from pyramid_beaker import set_cache_regions_from_settings
from beaker.cache import cache_region
from sqlalchemy import engine_from_config
from gmusicapi import Mobileclient, Webclient

from .models import (
    DBSession,
    Base,
    Song,
    Album,
    Artist,
)

logger = logging.getLogger(__name__)
gm = Mobileclient()
wc = Webclient()
check_username = lambda: False


@cache_region("long_term")
def get_song(song_id):
    f = NamedTemporaryFile(prefix=song_id + str(time.time()),
                           suffix='.mp3', delete=True)
    f.write(wc.get_stream_audio(song_id))
    return FileResponse(f.name)


@cache_region("long_term")
def get_artwork(song_id):
    f = NamedTemporaryFile(prefix=song_id + str(time.time()),
                           suffix='.jpg', delete=True)
    song = DBSession.query(Song).filter(Song.id == song_id).first()
    f.write(song.album.artwork)
    return FileResponse(f.name)


@cache_region("default_term")
def get_all_songs():
    return gm.get_all_songs()


@cache_region("default_term")
def get_all_playlist_ids():
    playlistids = {}
    try:
        playlistids = gm.get_all_playlist_ids(auto=False)['user']
    except Exception:
        pass
    return playlistids


@cache_region("default_term")
def get_playlist_songs(playlist_id):
    return gm.get_playlist_songs(playlist_id)


def load_songs_into_database():
    print "Downloading song list..."
    songs = gm.get_all_songs()
    total = len(songs)
    current_number = 0
    for song in songs:
        #print current_number, "/", total
        sys.stdout.write("\r[%s->%s] - %d%% (%d/%d)" % (
            "#" * int(current_number/float(total)*25),
            " " * int(25 - (current_number/float(total)*25)),
            int(current_number/float(total)*100),
            current_number,
            total,
        ))
        sys.stdout.flush()
        current_number += 1
        existing_song = DBSession.query(Song).filter(
            Song.source == "Google Music"
        ).filter(
            Song.location == song.get('id')
        ).first()
        existing_album = DBSession.query(Album).filter(
            Album.name == song.get('album')
        ).first()
        existing_artist = DBSession.query(Artist).filter(
            Artist.name == song.get('artist')
        ).first()
        if not existing_artist:
            new_artist = Artist()
            new_artist.name = song.get('artist')
            new_artist.genre = song.get('genre')
            if len(song.get('artistArtRef', [])) > 0:
                new_artist.artwork = urllib.urlopen(
                    song.get('artistArtRef')[0]['url']
                ).read()
            DBSession.add(new_artist)
        if not existing_album:
            artist = DBSession.query(Artist).filter(
                Artist.name == song.get('artist')
            ).first()
            new_album = Album()
            new_album.name = song.get('album')
            new_album.disc_number = song.get('discNumber')
            new_album.year = song.get('year')
            new_album.album_artist = song.get('albumArtist')
            new_album.total_track_count = song.get('totalTrackCount')
            new_album.artist = artist
            if len(song.get('albumArtRef', [])) > 0:
                new_album.artwork = urllib.urlopen(
                    song.get('albumArtRef')[0]['url']
                ).read()
            DBSession.add(new_album)
        if not existing_song:
            album = DBSession.query(Album).filter(
                Album.name == song.get('album')
            ).first()
            new_song = Song()
            new_song.source = "Google Music"
            new_song.location = song.get('id')
            new_song.title = song.get('title')
            new_song.rating = song.get('rating')
            new_song.track = song.get('trackNumber')
            new_song.play_count = song.get('playCount')
            new_song.duration = int(int(song.get('durationMillis')) / 1000)
            new_song.album = album
            DBSession.add(new_song)
        DBSession.flush()
        transaction.commit()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    global check_username

    check_username = lambda username, password:\
        settings['gmusicapi_username'] == username and\
        settings['gmusicapi_password'] == password
    if not gm.login(settings['gmusicapi_username'],
                    settings['gmusicapi_password']):
        logger.warn("Unable to login to Google Music!")
        exit()
    if not wc.login(settings['gmusicapi_username'],
                    settings['gmusicapi_password']):
        logger.warn("Unable to login to Google Music!")
        exit()

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('gmusic.views')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.scan()
    return config.make_wsgi_app()
