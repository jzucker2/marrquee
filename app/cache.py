import os
import time
from enum import Enum
from typing import List, Dict
from .utils import LogHelper


log = LogHelper.get_env_logger(__name__)


class CacheTarget(str, Enum):
    MOVIES = "movies"
    CUSTOM = "custom"
    BOTH = "both"


# Configuration
DEFAULT_CACHE_DIR = "/data/assets"
DEFAULT_MAX_CACHE_AGE = 60 * 60 * 24 * 7  # 1 week
MAX_CACHE_AGE = int(os.environ.get(
    'MAX_CACHE_AGE',
    DEFAULT_MAX_CACHE_AGE
))


class CustomCache:
    SUBFOLDERS: Dict[CacheTarget, str] = {
        CacheTarget.MOVIES: "movies",
        CacheTarget.CUSTOM: "custom"
    }

    def __init__(
        self,
        cache_dir: str = DEFAULT_CACHE_DIR,
        set_up_cache_dirs: bool = True,
    ):
        super().__init__()
        self._cache_dir = cache_dir
        if set_up_cache_dirs:
            self.setup_cache_dirs()

    @property
    def cache_dir(self):
        return self._cache_dir

    def cache_dirs(self, target: CacheTarget) -> List[str]:
        """
        Returns one or more cache directories based on the CacheTarget.
        - BOTH returns all subfolders.
        - MOVIES or CUSTOM returns a single subfolder.
        """
        if target == CacheTarget.BOTH:
            return [os.path.join(self.cache_dir, subfolder)
                    for subfolder in self.SUBFOLDERS.values()]
        elif target in self.SUBFOLDERS:
            return [os.path.join(self.cache_dir, self.SUBFOLDERS[target])]
        else:
            raise ValueError(f"Unsupported CacheTarget: {target}")

    def setup_cache_dirs(self) -> None:
        """Ensure all cache directories exist."""
        log.debug(f"ensure directories self.cache_dir: {self.cache_dir}")
        os.makedirs(self.cache_dir, exist_ok=True)
        for folder in self.cache_dirs(CacheTarget.BOTH):
            os.makedirs(folder, exist_ok=True)

    def clean_cache(self, target: CacheTarget = CacheTarget.BOTH) -> None:
        """Delete cache files older than MAX_CACHE_AGE
        in specified folder(s)."""
        now = time.time()
        for folder in self.cache_dirs(target):
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if (os.path.isfile(filepath) and
                        now - os.path.getmtime(filepath) > MAX_CACHE_AGE):
                    os.remove(filepath)

    def clear_cache(self, target: CacheTarget = CacheTarget.BOTH) -> None:
        """Delete cache files older than MAX_CACHE_AGE
        in specified folder(s)."""
        for folder in self.cache_dirs(target):
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                os.remove(filepath)

    def get_file_path(self, filename: str, target: CacheTarget) -> str:
        """
        Returns the full path to the file in the specified target folder.
        Assumes only one folder is relevant for non-BOTH targets.
        """
        folders = self.cache_dirs(target)
        if len(folders) != 1:
            e_m = f"Expected a single folder for {target}, got multiple."
            raise ValueError(e_m)
        return os.path.join(folders[0], filename)

    def get_all_files(self, target: CacheTarget = CacheTarget.BOTH) -> List[str]:  # noqa: E501
        """Returns list of full paths to all .jpg
        files in the specified cache folder(s)."""
        all_files = []
        for folder in self.cache_dirs(target):
            try:
                all_files += [
                    os.path.join(folder, f)
                    for f in os.listdir(folder)
                    if f.endswith(".jpg")
                ]
            except FileNotFoundError:
                continue  # Folder may not exist yet, skip it gracefully
        return all_files
