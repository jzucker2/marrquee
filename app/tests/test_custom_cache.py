import os
import time
import tempfile
import shutil
import pytest
from pathlib import Path

from ..cache import CustomCache, CacheTarget  # Replace with actual path


@pytest.fixture(scope="function")
def temp_cache():
    """Provides a temp CustomCache instance and cleans up after test."""
    temp_dir = tempfile.mkdtemp()
    cache = CustomCache(cache_dir=temp_dir)
    yield cache
    shutil.rmtree(temp_dir)


def test_cache_dirs_resolve_correctly(temp_cache):
    movie_dirs = temp_cache.cache_dirs(CacheTarget.MOVIES)
    custom_dirs = temp_cache.cache_dirs(CacheTarget.CUSTOM)
    both_dirs = temp_cache.cache_dirs(CacheTarget.BOTH)

    assert len(movie_dirs) == 1
    assert len(custom_dirs) == 1
    assert len(both_dirs) == 2
    assert all(os.path.exists(d) for d in both_dirs)


def test_get_file_path_returns_expected_path(temp_cache):
    filename = "test.jpg"
    path = temp_cache.get_file_path(filename, CacheTarget.CUSTOM)
    assert path.endswith(f"{CacheTarget.CUSTOM.value}/{filename}")
    assert isinstance(path, str)


def test_get_all_files_lists_only_jpgs(temp_cache):
    custom_dir = temp_cache.cache_dirs(CacheTarget.CUSTOM)[0]
    movie_dir = temp_cache.cache_dirs(CacheTarget.MOVIES)[0]

    Path(os.path.join(custom_dir, "a.jpg")).write_text("fake")
    Path(os.path.join(movie_dir, "b.jpg")).write_text("fake")
    Path(os.path.join(movie_dir, "not_an_image.txt")).write_text("skip")

    files_custom = temp_cache.get_all_files(CacheTarget.CUSTOM)
    files_movies = temp_cache.get_all_files(CacheTarget.MOVIES)
    files_both = temp_cache.get_all_files(CacheTarget.BOTH)

    assert len(files_custom) == 1
    assert files_custom[0].endswith("a.jpg")
    assert len(files_movies) == 1
    assert files_movies[0].endswith("b.jpg")
    assert len(files_both) == 2


def test_clean_cache_removes_old_files(temp_cache):
    movie_dir = temp_cache.cache_dirs(CacheTarget.MOVIES)[0]
    test_file = os.path.join(movie_dir, "old.jpg")

    with open(test_file, "w") as f:
        f.write("data")

    # Modify file time to simulate old file
    old_time = time.time() - (60 * 60 * 24 * 8)  # 8 days ago
    os.utime(test_file, (old_time, old_time))

    assert os.path.exists(test_file)
    temp_cache.clean_cache(CacheTarget.MOVIES)
    assert not os.path.exists(test_file)


def test_get_file_path_raises_for_both(temp_cache):
    with pytest.raises(ValueError):
        temp_cache.get_file_path("file.jpg", CacheTarget.BOTH)
