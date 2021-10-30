"""Utilities for managing the cache."""

import json
from pathlib import Path

from beartype import beartype

from .constants import CACHE_README_TEXT, KEY_NAME_DATA, KEY_NAME_META, TEST_DATA_TYPE


@beartype
def init_cache(path_cache_dir: Path) -> None:
    """Ensure that the cache directory exists and add the README.

    Args:
        path_cache_dir: location of the cache directory

    """
    path_cache_dir.mkdir(exist_ok=True, parents=True)
    (path_cache_dir / 'README.md').write_text(CACHE_README_TEXT)


@beartype
def cache_data(path_cache_file: Path, metadata: dict, test_data: TEST_DATA_TYPE) -> None:
    """Cache the specified data.

    Args:
        path_cache_file: location of the cache file to write
        metadata: metadata dictionary to store in the cache file
        test_data: arbitrary test data to store

    """
    cache_dict = {KEY_NAME_META: metadata, KEY_NAME_DATA: test_data}
    path_cache_file.parent.mkdir(exist_ok=True, parents=True)
    _json = json.dumps(cache_dict, sort_keys=True, indent=2, separators=(',', ': '))
    path_cache_file.write_text(_json.strip() + '\n')


@beartype
def load_cached_data(path_cache_file: Path) -> TEST_DATA_TYPE:
    """Cache the specified data.

    Args:
        path_cache_file: location of the cache file to write

    Returns:
        TEST_DATA_TYPE: loaded data from cache file

    """
    cache_dict = json.load(path_cache_file.open('r'))
    return cache_dict[KEY_NAME_DATA]


@beartype
def resolve_cache_name(test_dir: Path, test_file: Path, parameter_index: int) -> str:
    """Resolve the cache file path based on test information.

    Args:
        test_dir: location of the test directory
        test_file: location of the test file
        parameter_index: index of the parameter in the test function

    Returns:
        str: cache_name

    """
    partial_path = '/'.join([*test_file.parent.relative_to(test_dir).parts] + [test_file.stem])
    return f'{partial_path}-{parameter_index:02d}.json'
