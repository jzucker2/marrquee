from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
import aiohttp
from PIL import Image
from io import BytesIO
from typing import List
import uuid
import random
import os
from .utils import LogHelper
from .version import version
from .plex import get_random_movie_poster
from .cache import CacheTarget,  CustomCache


RESIZE_MAX_DIM = 512


log = LogHelper.get_env_logger(__name__)


app = FastAPI()


Instrumentator().instrument(app).expose(app)


IMAGE_CACHE = CustomCache()


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


async def download_and_process_image(url: str, target: CacheTarget = CacheTarget.MOVIES) -> str:  # noqa: E501
    """Download from the URL, resize and convert to JPEG, and save."""
    log.debug(f"fetching image from url: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(
                    status_code=resp.status,
                    detail="Failed to fetch image")
            content = await resp.read()

    try:
        img = Image.open(BytesIO(content))
        img = img.convert("RGB")
        img.thumbnail((RESIZE_MAX_DIM, RESIZE_MAX_DIM))

        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = IMAGE_CACHE.get_file_path(
            filename,
            target=target)
        img.save(filepath, "JPEG", quality=85)
        log.debug(f"Saved image from url: {url} to "
                  f"filepath: {filepath} with filename: {filename}")

        return filename
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image processing failed: {str(e)}")


@app.get("/cache-poster")
async def cache_random_poster():
    IMAGE_CACHE.clean_cache(target=CacheTarget.MOVIES)
    random_movie_info = get_random_movie_poster()
    log.debug(f"redirect => random_movie_info: {random_movie_info}")
    actual_poster_url = random_movie_info['poster_url']
    filename = await download_and_process_image(actual_poster_url)
    return FileResponse(
        IMAGE_CACHE.get_file_path(filename, target=CacheTarget.MOVIES),
        media_type="image/jpeg",
        filename=filename)


@app.get("/random-cached-poster")
def get_random_cached_poster():
    files = IMAGE_CACHE.get_all_files(target=CacheTarget.MOVIES)
    if not files:
        raise HTTPException(
            status_code=404,
            detail="No cached images available")
    filename = random.choice(files)
    return FileResponse(
        IMAGE_CACHE.get_file_path(filename, target=CacheTarget.MOVIES),
        media_type="image/jpeg",
        filename=filename)


@app.post("/cache-custom-image")
async def cache_custom_image(req: ImageRequest):
    IMAGE_CACHE.clean_cache(target=CacheTarget.CUSTOM)

    filename = await download_and_process_image(req.url)
    log.debug(f"custom => download and processed filename: {filename}")
    return FileResponse(
        IMAGE_CACHE.get_file_path(filename, target=CacheTarget.CUSTOM),
        media_type="image/jpeg",
        filename=filename)


@app.get("/random-cached-custom")
def get_random_cached_custom_image():
    files = IMAGE_CACHE.get_all_files(target=CacheTarget.CUSTOM)
    if not files:
        raise HTTPException(
            status_code=404,
            detail="No cached images available")
    filename = random.choice(files)
    return FileResponse(
        IMAGE_CACHE.get_file_path(filename, target=CacheTarget.CUSTOM),
        media_type="image/jpeg",
        filename=filename)


@app.get("/images", response_model=List[str])
def list_images(target: CacheTarget = Query(CacheTarget.BOTH)):  # noqa: E501
    """List image files from the specified cache folder(s)."""
    files = IMAGE_CACHE.get_all_files(target=target)
    return [os.path.basename(f) for f in files]


@app.get("/random-image", response_model=List[str])
def random_image(target: CacheTarget = Query(CacheTarget.BOTH)):  # noqa: E501
    """List image files from the specified cache folder(s)."""
    files = IMAGE_CACHE.get_all_files(target=target)
    if not files:
        raise HTTPException(
            status_code=404,
            detail="No cached images available")
    filename = random.choice(files)
    return FileResponse(
        IMAGE_CACHE.get_file_path(filename, target=target),
        media_type="image/jpeg",
        filename=filename)


@app.get("/images/{image_id}")
def get_image(image_id: str, target: CacheTarget = Query("both", description="movies, custom, or both")):  # noqa: E501
    """Serve image file by filename from the specified folder(s)."""
    for folder in IMAGE_CACHE.cache_dirs(target=target):
        filepath = os.path.join(folder, image_id)
        if os.path.isfile(filepath):
            return FileResponse(filepath, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="File not found")
