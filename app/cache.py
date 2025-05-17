import os
import time
from enum import Enum, auto
from typing import List, Dict


class CacheTarget(str, Enum):
    MOVIES = "movies"
    CUSTOM = "custom"
    BOTH = "both"


# Configuration
BASE_CACHE_DIR = "/data/assets"
MAX_CACHE_AGE = 60 * 60 * 6  # 6 hours
METADATA_FILE = os.path.join(BASE_CACHE_DIR, "metadata.json")


class CustomCache:
    SUBFOLDERS: Dict[CacheTarget, str] = {
        CacheTarget.MOVIES: "movies",
        CacheTarget.CUSTOM: "custom"
    }

    @classmethod
    def cache_dirs(cls, target: CacheTarget) -> List[str]:
        """
        Returns one or more cache directories based on the CacheTarget.
        - BOTH returns all subfolders.
        - MOVIES or CUSTOM returns a single subfolder.
        """
        if target == CacheTarget.BOTH:
            return [os.path.join(BASE_CACHE_DIR, subfolder)
                    for subfolder in cls.SUBFOLDERS.values()]
        elif target in cls.SUBFOLDERS:
            return [os.path.join(BASE_CACHE_DIR, cls.SUBFOLDERS[target])]
        else:
            raise ValueError(f"Unsupported CacheTarget: {target}")

    @classmethod
    def setup_cache_dirs(cls) -> None:
        """Ensure all cache directories exist."""
        os.makedirs(BASE_CACHE_DIR, exist_ok=True)
        for folder in cls.cache_dirs(CacheTarget.BOTH):
            os.makedirs(folder, exist_ok=True)

    @classmethod
    def clean_cache(cls, target: CacheTarget = CacheTarget.BOTH) -> None:
        """Delete cache files older than MAX_CACHE_AGE in specified folder(s)."""
        now = time.time()
        for folder in cls.cache_dirs(target):
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath) and now - os.path.getmtime(filepath) > MAX_CACHE_AGE:
                    os.remove(filepath)

    @classmethod
    def get_file_path(cls, filename: str, target: CacheTarget) -> str:
        """
        Returns the full path to the file in the specified target folder.
        Assumes only one folder is relevant for non-BOTH targets.
        """
        folders = cls.cache_dirs(target)
        if len(folders) != 1:
            raise ValueError(f"Expected a single folder for {target}, got multiple.")
        return os.path.join(folders[0], filename)

    @classmethod
    def get_all_files(cls, target: CacheTarget = CacheTarget.BOTH) -> List[str]:
        """Returns list of full paths to all .jpg files in the specified cache folder(s)."""
        all_files = []
        for folder in cls.cache_dirs(target):
            try:
                all_files += [
                    os.path.join(folder, f)
                    for f in os.listdir(folder)
                    if f.endswith(".jpg")
                ]
            except FileNotFoundError:
                continue  # Folder may not exist yet, skip it gracefully
        return all_files


# Initialize cache directories
CustomCache.setup_cache_dirs()
