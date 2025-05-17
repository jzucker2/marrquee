from fastapi import FastAPI

from .version import version

from prometheus_fastapi_instrumentator import Instrumentator


from .utils import LogHelper
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
