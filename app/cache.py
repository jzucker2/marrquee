import os
import time
from enum import Enum, auto
from typing import List


class CacheTarget(Enum):
    MOVIES = auto()
    CUSTOM = auto()
    BOTH = auto()


# Configuration
BASE_CACHE_DIR = "/data/assets"
MAX_CACHE_AGE = 60 * 60 * 6  # 6 hours
METADATA_FILE = os.path.join(BASE_CACHE_DIR, "metadata.json")


class CustomCache:
    SUBFOLDERS = {
        CacheTarget.MOVIES: "movies",
        CacheTarget.CUSTOM: "custom"
    }

    @classmethod
    def cache_dirs(cls, target: CacheTarget) -> List[str]:
        """Return list of cache directories based on target."""
        if target == CacheTarget.BOTH:
            return [os.path.join(BASE_CACHE_DIR, folder)
                    for folder in cls.SUBFOLDERS.values()]
        else:
            return [os.path.join(BASE_CACHE_DIR, cls.SUBFOLDERS[target])]

    @classmethod
    def setup_cache_dirs(cls):
        """Ensure all cache directories exist."""
        os.makedirs(BASE_CACHE_DIR, exist_ok=True)
        for path in cls.cache_dirs(CacheTarget.BOTH):
            os.makedirs(path, exist_ok=True)

    @classmethod
    def clean_cache(cls, target: CacheTarget = CacheTarget.BOTH):
        """Delete cache files older than MAX_CACHE_AGE."""
        now = time.time()
        for folder in cls.cache_dirs(target):
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if (os.path.isfile(filepath) and
                        now - os.path.getmtime(filepath) > MAX_CACHE_AGE):
                    os.remove(filepath)

    @classmethod
    def get_file_path(cls, filename: str, target: CacheTarget) -> str:
        """Get full file path in the specified cache folder."""
        folder = cls.cache_dirs(target)[0]
        return os.path.join(folder, filename)

    @classmethod
    def get_all_files(cls, target: CacheTarget = CacheTarget.BOTH) -> List[str]:  # noqa: E501
        """Get all .jpg files in the specified cache folder(s)."""
        files = []
        for folder in cls.cache_dirs(target):
            files += [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.endswith(".jpg")
            ]
        return files


# Ensure folders are initialized
CustomCache.setup_cache_dirs()
