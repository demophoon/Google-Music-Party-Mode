import logging
import string
import random
from functools import wraps

from pyramid.httpexceptions import HTTPUnauthorized, HTTPFound
from pyramid.response import Response
from pyramid.view import view_config

from gmusic import (
    get_all_songs,
    get_all_playlist_ids,
    get_playlist_songs,
    get_song,
    get_artwork,
    check_username,
    wc,
)
from .models import (
    DBSession,
    _settings,
    Song,
)

logger = logging.getLogger(__name__)
currently_logged_in_token = None


def authorize():
    def authorize_decorator(view_func):
        logger.info("Decorator called")

        def _decorator(view, *args, **kwargs):
            auth_token = view.cookies.get("auth-token")
            logger.info(view.cookies)
            if auth_token and auth_token == currently_logged_in_token:
                return view_func(view, *args, **kwargs)
            else:
                raise HTTPUnauthorized
        return wraps(view_func)(_decorator)
    return authorize_decorator


@view_config(renderer="templates/login.pt", context=HTTPUnauthorized)
def login_view(request):
    return {}


@view_config(route_name="api_login", renderer="json", request_method="POST")
def api_login(request):
    global currently_logged_in_token
    username = request.POST.get("username")
    password = request.POST.get("password")
    if check_username(username, password):
        chars = string.ascii_letters + string.digits
        token = [random.choice(chars) for x in xrange(60)]
        currently_logged_in_token = ''.join(token)
        raise HTTPFound(location="/", headers=[(
            'Set-Cookie', 'auth-token=' + currently_logged_in_token
        )])
    else:
        raise HTTPUnauthorized


@view_config(route_name='api_get_all_songs', renderer="json")
def api_get_all_songs(request):
    page = int(request.params.get("page", 0))
    items = int(request.params.get("items", 1000))
    songs = []
    songs = get_all_songs()
    #playlist_names = get_all_playlist_ids()
    #for name in playlist_names:
    #    for pid in playlist_names[name]:
    #        for song in get_playlist_songs(pid):
    #            if song not in songs:
    #                songs.append(song)
    return songs[page * items:(page + 1) * items]


@view_config(route_name='api_get_song', renderer="json")
def api_get_song(request):
    id = request.params.get("song_id")
    if id:
        response = get_song(id)
        return response
    return False


@view_config(route_name='api_get_artwork', renderer="json")
def api_get_artwork(request):
    id = request.params.get("song_id")
    if id:
        response = get_artwork(id)
        return response
    return False


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def index(request):
    return {"device_id": _settings.get_device_id()}


@view_config(route_name='settings', renderer='templates/settings.pt')
def settings(request):
    return {"device_id": _settings.get_device_id()}


@view_config(route_name='api_get_registered_devices', renderer="json", request_method="GET")
def api_get_registered_devices(request):
    return wc.get_registered_devices()


@view_config(route_name='api_get_registered_devices', renderer="json", request_method="POST")
def api_post_registered_devices(request):
    device_id = request.POST['device_id']
    _settings.set_device_id(device_id)
    return _settings.get_device_id()


def includeme(config):
    config.add_route('home', '/')
    config.add_route('settings', '/settings')
    config.add_route('api_login', '/login')
    config.add_route('api_get_all_songs', '/api/v1/songs')
    config.add_route('api_get_song', '/api/v1/song')
    config.add_route('api_get_artwork', '/api/v1/artwork')

    config.add_route('api_get_registered_devices', '/api/v1/devices')
