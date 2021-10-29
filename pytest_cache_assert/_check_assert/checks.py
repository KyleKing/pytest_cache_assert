"""Assertion checks for unit tests."""

from pathlib import Path

from beartype import beartype

from .caching import cache_data, init_cache, load_cached_data
from .constants import TEST_DATA_TYPE


# FIXME: path_cache_file should be discovered through introspection if None
@beartype
def check_assert(
    test_data: TEST_DATA_TYPE, path_cache_file: Path,
    path_cache_dir: Path,
) -> None:
    """Core logic for pytest_cache_assert to handle caching and assertion-checking.

    Will raise AssertionError if any assertion fails.

    Args:
        test_data: dictionary to test and/or cache
        path_cache_file: location of the cache file to write. Default is None and will be resolved through introspection
        path_cache_dir: location of the cache directory. TODO: set in global configuration

    """
    if not path_cache_dir.is_dir():
        init_cache(path_cache_dir)
    if not path_cache_file.is_file():
        # TODO: Generate metadata based on pytest parameters/introspection
        cache_data(path_cache_file, {}, test_data)
    cached_data = load_cached_data(path_cache_file)

    # TODO: Start with basic assertion and implement rest of complexity later
    assert test_data == cached_data  # noqa: B101,S101
