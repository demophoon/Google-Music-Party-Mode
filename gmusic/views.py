from pyramid.view import view_config

from gmusic import (
    get_all_songs,
    get_all_playlist_ids,
    get_playlist_songs,
    get_song,
)
from .models import (
    DBSession,
)


@view_config(route_name='api_get_all_songs', renderer="json")
def api_get_all_songs(request):
    songs = []
    songs = get_all_songs()
    return songs


@view_config(route_name='api_get_song', renderer="json")
def api_get_song(request):
    id = request.params.get("song_id")
    if id:
        response = get_song(id)
        return response
    return False


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def index(request):
    return {}


def includeme(config):
    config.add_route('home', '/')
    config.add_route('api_get_all_songs', '/api/v1/songs')
    config.add_route('api_get_song', '/api/v1/song')
