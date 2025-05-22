from plexapi.server import PlexServer
import random
import os
from .utils import LogHelper


log = LogHelper.get_env_logger(__name__)


BASE_URL = os.environ.get("PLEX_BASE_URL")
TOKEN = os.environ.get("PLEX_TOKEN")


class PlexClient:
    _plex = None

    @classmethod
    def _get_plex(cls):
        if cls._plex is None:
            try:
                log.debug(f'Plex BASE_URL: {BASE_URL}')
                cls._plex = PlexServer(BASE_URL, TOKEN)
                log.debug("Initialized PlexServer client.")
            except Exception as e:
                log.error(f"Failed to initialize PlexServer: {e}")
                raise
        return cls._plex

    @classmethod
    def get_random_movie_poster(cls):
        movies = cls._get_plex().library.section('Movies').all()
        random_movie = random.choice(movies)
        log.debug(f'Plex random_movie: {random_movie}')
        poster_url = f"{BASE_URL}{random_movie.thumb}?X-Plex-Token={TOKEN}"
        log.debug(f'Plex random_movie: {random_movie} => poster_url: {poster_url}')

        return {
            "title": random_movie.title,
            "poster_url": poster_url
        }

    @classmethod
    def get_manual_movie_poster(cls, movie_title):
        try:
            movie = cls._get_plex().library.section('Movies').get(movie_title)
            log.debug(f'Plex movie: {movie}')
            poster_url = f"{BASE_URL}{movie.thumb}?X-Plex-Token={TOKEN}"
            log.debug(f'Plex movie: {movie} => poster_url: {poster_url}')

            return {
                "title": movie.title,
                "poster_url": poster_url
            }
        except Exception as e:
            log.error(f"Failed to find movie '{movie_title}': {e}")
            return {
                "error": f"Movie '{movie_title}' not found."
            }
