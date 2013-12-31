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
    check_username,
)
from .models import (
    DBSession,
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
    songs = get_all_songs()[page * items:(page + 1) * items]
    return songs


@view_config(route_name='api_get_song', renderer="json")
@authorize()
def api_get_song(request):
    id = request.params.get("song_id")
    if id:
        response = get_song(id)
        return response
    return False


@view_config(route_name='home', renderer='templates/mytemplate.pt')
@authorize()
def index(request):
    return {}


def includeme(config):
    config.add_route('home', '/')
    config.add_route('api_login', '/login')
    config.add_route('api_get_all_songs', '/api/v1/songs')
    config.add_route('api_get_song', '/api/v1/song')
