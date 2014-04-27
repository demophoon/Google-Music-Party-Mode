import logging
import time
import urllib
from tempfile import NamedTemporaryFile

from pyramid.config import Configurator
from pyramid.response import FileResponse
from pyramid_beaker import set_cache_regions_from_settings
from beaker.cache import cache_region
from sqlalchemy import engine_from_config
from gmusicapi import Mobileclient, Webclient

from .models import (
    DBSession,
    Base,
    _settings,
)

logger = logging.getLogger(__name__)
gm = Mobileclient()
wc = Webclient()
check_username = lambda: False


@cache_region("long_term")
def get_song(song_id):
    f = NamedTemporaryFile(prefix=song_id + str(time.time()),
                           suffix='.mp3', delete=True)
    f.write(urllib.urlopen(
        gm.get_stream_url(song_id, _settings.get_device_id()[2:])
    ).read())
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
