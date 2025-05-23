from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from typing import List
import random
import os
from .utils import LogHelper
from .version import version
from .plex import PlexClient
from .cache import CacheTarget, CustomCache
from .image_processor import ImageProcessor


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
    return PlexClient.get_random_movie_poster()


@app.get("/random-poster-redirect")
def redirect_to_poster():
    random_movie_info = PlexClient.get_random_movie_poster()
    log.debug(f"redirect => random_movie_info: {random_movie_info}")
    actual_poster_url = random_movie_info['poster_url']
    log.debug(f"redirect => actual_poster_url: {actual_poster_url}")
    return RedirectResponse(actual_poster_url)


class ImageRequest(BaseModel):
    url: str


class ManualPosterRequest(BaseModel):
    movie_title: str


@app.get("/cache-poster")
async def cache_random_poster():
    IMAGE_CACHE.clean_cache(target=CacheTarget.MOVIES)
    random_movie_info = PlexClient.get_random_movie_poster()
    log.debug(f"cache => random_movie_info: {random_movie_info}")
    actual_poster_url = random_movie_info['poster_url']
    filename = await ImageProcessor.download_and_process_image(
        actual_poster_url,
        IMAGE_CACHE)
    log.debug(f'random_movie_info: {random_movie_info} '
              f'got filename: {filename}')
    return FileResponse(
        IMAGE_CACHE.get_file_path(filename, target=CacheTarget.MOVIES),
        media_type="image/png",
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
        media_type="image/png",
        filename=filename)


@app.post("/cache-manual-poster")
async def cache_manual_poster(req: ManualPosterRequest):
    IMAGE_CACHE.clean_cache(target=CacheTarget.MOVIES)
    manual_movie_info = PlexClient.get_manual_movie_poster(req.movie_title)
    log.debug(f"cache => manual_movie_info: {manual_movie_info}")
    actual_poster_url = manual_movie_info['poster_url']
    filename = await ImageProcessor.download_and_process_image(
        actual_poster_url,
        IMAGE_CACHE)
    log.debug(f'manual_movie_info: {manual_movie_info} '
              f'got filename: {filename}')
    return FileResponse(
        IMAGE_CACHE.get_file_path(filename, target=CacheTarget.MOVIES),
        media_type="image/png",
        filename=filename)


@app.post("/cache-custom-image")
async def cache_custom_image(req: ImageRequest):
    IMAGE_CACHE.clean_cache(target=CacheTarget.CUSTOM)

    filename = await ImageProcessor.download_and_process_image(
        req.url,
        IMAGE_CACHE,
        target=CacheTarget.CUSTOM)
    log.debug(f"custom => download and processed filename: {filename}")
    return FileResponse(
        IMAGE_CACHE.get_file_path(filename, target=CacheTarget.CUSTOM),
        media_type="image/png",
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
        media_type="image/png",
        filename=filename)


@app.get("/images", response_model=List[str])
def list_images(target: CacheTarget = Query(CacheTarget.BOTH)):
    """List image files from the specified cache folder(s)."""
    files = IMAGE_CACHE.get_all_files(target=target)
    return [os.path.basename(f) for f in files]


@app.get("/random-image", response_model=List[str])
def random_image(target: CacheTarget = Query(CacheTarget.BOTH)):
    """List image files from the specified cache folder(s)."""
    files = IMAGE_CACHE.get_all_files(target=target)
    if not files:
        raise HTTPException(
            status_code=404,
            detail="No cached images available")
    filename = random.choice(files)
    return FileResponse(
        IMAGE_CACHE.get_file_path(filename, target=target),
        media_type="image/png",
        filename=filename)


@app.get("/images/{image_id}")
def get_image(image_id: str, target: CacheTarget = Query(CacheTarget.BOTH)):
    """Serve image file by filename from the specified folder(s)."""
    for folder in IMAGE_CACHE.cache_dirs(target=target):
        filepath = os.path.join(folder, image_id)
        if os.path.isfile(filepath):
            return FileResponse(filepath, media_type="image/png")
    raise HTTPException(status_code=404, detail="File not found")


@app.post("/cache/clear")
def clear_cache(target: CacheTarget = Query(CacheTarget.BOTH)):
    """Clear the cache from the specified folder(s)."""
    IMAGE_CACHE.clear_cache(target=target)
    return {"status": "success", "cleared": target}
