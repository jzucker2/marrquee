from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
import aiohttp
from PIL import Image
import os
import time
from io import BytesIO
import uuid
import random
from .utils import LogHelper
from .version import version
from .plex import get_random_movie_poster


# Configuration
CACHE_DIR = "/data/assets"
MAX_CACHE_AGE = 60 * 60 * 6  # 6 hours
METADATA_FILE = os.path.join(CACHE_DIR, "metadata.json")
RESIZE_MAX_DIM = 512
os.makedirs(CACHE_DIR, exist_ok=True)


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


class ImageRequest(BaseModel):
    url: str


def clean_cache():
    """Delete cache files older than MAX_CACHE_AGE."""
    now = time.time()
    for filename in os.listdir(CACHE_DIR):
        filepath = os.path.join(CACHE_DIR, filename)
        if os.path.isfile(filepath) and now - os.path.getmtime(filepath) > MAX_CACHE_AGE:
            os.remove(filepath)


async def download_and_process_image(url: str) -> str:
    """Download from the hardcoded URL, resize and convert to JPEG, and save."""
    log.debug(f"fetching image from url: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail="Failed to fetch image")
            content = await resp.read()

    try:
        img = Image.open(BytesIO(content))
        img = img.convert("RGB")
        img.thumbnail((RESIZE_MAX_DIM, RESIZE_MAX_DIM))

        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(CACHE_DIR, filename)
        img.save(filepath, "JPEG", quality=85)

        return filename
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")


@app.get("/cache-poster")
async def cache_random_poster():
    clean_cache()
    random_movie_info = get_random_movie_poster()
    log.debug(f"redirect => random_movie_info: {random_movie_info}")
    actual_poster_url = random_movie_info['poster_url']
    filename = await download_and_process_image(actual_poster_url)
    return FileResponse(os.path.join(CACHE_DIR, filename), media_type="image/jpeg", filename=filename)


@app.get("/random-cached-poster")
def get_random_cached_poster():
    clean_cache()
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".jpg")]
    if not files:
        raise HTTPException(status_code=404, detail="No cached images available")
    filename = random.choice(files)
    return FileResponse(os.path.join(CACHE_DIR, filename), media_type="image/jpeg", filename=filename)
