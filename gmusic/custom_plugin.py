import os
import urllib
import logging

from pyramid.response import FileResponse
from beaker.cache import cache_region

import gmusic

from .models import _settings

logger = logging.getLogger(__name__)
cache_dir = "./cache/"


@cache_region("default_term")
def get_song_patched(song_id):
    logger.warn("##### USING MODIFIED SONG DOWNLOADER! #####")
    file_path = cache_dir + song_id + ".mp3"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    if not os.path.isfile(file_path):
        f = open(file_path, "w")
        f.write(urllib.urlopen(
            gmusic.gm.get_stream_url(song_id, _settings.get_device_id()[2:])
        ).read())
        f.close()
    return FileResponse(file_path)


def includeme(config):
    gmusic.get_song = get_song_patched
    logger.warn("##### SONG DOWNLOADER IS PATCHED! #####")
