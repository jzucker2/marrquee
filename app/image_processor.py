from fastapi import HTTPException
import aiohttp
from PIL import Image, ImageFile
from PIL.ImageFile import Imae
from io import BytesIO
import uuid
from .utils import LogHelper
from .cache import CustomCache, CacheTarget


log = LogHelper.get_env_logger(__name__)


RESIZE_MAX_DIM = 512


# Supported 7-color E-Ink palette
PALETTE = [
    (0, 0, 0),        # Black
    (255, 255, 255),  # White
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
]


class ImageProcessor:
    @classmethod
    def closest_color(cls, rgb):
        r, g, b = rgb
        return min(
            PALETTE,
            key=lambda c: (r - c[0]) ** 2 + (g - c[1]) ** 2 + (b - c[2]) ** 2)

    @classmethod
    def convert_image_for_eink(cls, input_path, output_path, size=(800, 480)):
        image = Image.open(input_path).convert('RGB')
        image = image.resize(size, Image.LANCZOS)

        # Create new image with optimized palette
        optimized = Image.new('RGB', image.size)
        pixels = optimized.load()
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                original = image.getpixel((x, y))
                pixels[x, y] = cls.closest_color(original)

        optimized.save(output_path, format='PNG')
        log.debug(f"Saved optimized image to {output_path}")
        return output_path

    @classmethod
    def _process_image_and_save(cls, image, output_path: str, size=(800, 480)):
        image = image.convert('RGB')
        image = image.thumbnail(size, Image.LANCZOS)

        # Create new image with optimized palette
        optimized = Image.new('RGB', image.size)
        pixels = optimized.load()
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                original = image.getpixel((x, y))
                pixels[x, y] = cls.closest_color(original)

        optimized.save(output_path, format='PNG')
        log.debug(f"Saved optimized image to {output_path}")
        return output_path

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

            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = custom_cache.get_file_path(
                filename,
                target=target)
            final_filename = cls._process_image_and_save(img, filepath)
            log.debug(f"Saved image from url: {url} to "
                      f"filepath: {filepath} with filename: {filename} "
                      f"at final_filename: {final_filename}")

            return filename
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image processing failed: {str(e)}")
