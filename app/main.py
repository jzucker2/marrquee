from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator


from .utils import LogHelper
from .version import version
from .plex import get_random_movie_poster


log = LogHelper.get_env_logger(__name__)


app = FastAPI()


Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/healthz")
def healthcheck():
    return {
        "message": "healthy",
        "version": version,
    }


@app.get("/random-poster")
def random_poster():
    return get_random_movie_poster()


@app.get("/random-poster-redirect")
def redirect_to_poster():
    random_movie_info = get_random_movie_poster()
    log.debug(f"redirect => random_movie_info: {random_movie_info}")
    actual_poster_url = random_movie_info['poster_url']
    log.debug(f"redirect => actual_poster_url: {actual_poster_url}")
    return RedirectResponse(actual_poster_url)
