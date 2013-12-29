import logging
import time
from tempfile import NamedTemporaryFile

from pyramid.config import Configurator
from pyramid.response import FileResponse
from pyramid_beaker import set_cache_regions_from_settings
from beaker.cache import cache_region
from sqlalchemy import engine_from_config
from gmusicapi import Webclient

from .models import (
    DBSession,
    Base,
)

logger = logging.getLogger(__name__)

gm = Webclient()
cache_dir = "./cache/"


@cache_region("long_term")
def get_song(song_id):
    f = NamedTemporaryFile(prefix=song_id + str(time.time()), suffix='.mp3', delete=True)
    f.write(gm.get_stream_audio(song_id))
    return FileResponse(f.name)


@cache_region("default_term")
def get_all_songs():
    return gm.get_all_songs()


@cache_region("default_term")
def get_all_playlist_ids():
    return gm.get_all_songs(auto=False)


@cache_region("default_term")
def get_playlist_songs(playlist_id):
    return gm.get_playlist_songs(playlist_id)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    if not gm.login(settings['gmusicapi_username'],
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
