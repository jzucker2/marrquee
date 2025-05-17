from plexapi.server import PlexServer
import random
import os
from .utils import LogHelper


log = LogHelper.get_env_logger(__name__)


BASE_URL = os.environ.get("PLEX_BASE_URL")
TOKEN = os.environ.get("PLEX_TOKEN")


plex = PlexServer(BASE_URL, TOKEN)


def get_random_movie_poster():
    movies = plex.library.section('Movies').all()
    random_movie = random.choice(movies)
    poster_url = f"{BASE_URL}{random_movie.thumb}?X-Plex-Token={TOKEN}"

    return {
        "title": random_movie.title,
        "poster_url": poster_url
    }
