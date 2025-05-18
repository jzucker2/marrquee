from fastapi import HTTPException
import aiohttp
from PIL import Image
from io import BytesIO
import uuid
from .utils import LogHelper
from .cache import CustomCache, CacheTarget


log = LogHelper.get_env_logger(__name__)


RESIZE_MAX_DIM = 512


class ImageProcessor:
    @classmethod
    async def download_and_process_image(cls, url: str, custom_cache: CustomCache, target: CacheTarget = CacheTarget.MOVIES) -> str:  # noqa: E501
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
            filepath = custom_cache.get_file_path(
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
