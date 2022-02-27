"""Utilities for managing the cache."""

import json
from pathlib import Path

from beartype import beartype
from beartype.typing import Any, Dict, List

from .constants import CACHE_README_TEXT, KEY_NAME_DATA, KEY_NAME_META, TEST_DATA_TYPE
from .serializer import CacheAssertSerializer


@beartype
def init_cache(path_cache_dir: Path) -> None:
    """Ensure that the cache directory exists and add the README.

    Args:
        path_cache_dir: location of the cache directory

    """
    path_cache_dir.mkdir(exist_ok=True, parents=True)
    (path_cache_dir / 'README.md').write_text(CACHE_README_TEXT)


@beartype
def _merge_metadata(new_metadata: Dict[str, Any], cached_meta_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge metadata for caching. Filter duplicates.

    Args:
        new_metadata: metadata dictionary to store in the cache file
        cached_meta_list: list of old metadata dictionaries to merging

    Returns:
        List[dict]: merged metadata

    """
    all_meta = [new_metadata, *cached_meta_list]
    unique_meta = {json.dumps(_m, sort_keys=True, cls=CacheAssertSerializer) for _m in all_meta}
    return [*map(json.loads, sorted(unique_meta))]


@beartype
def write_cache_data(path_cache_file: Path, metadata: Dict[str, Any], test_data: TEST_DATA_TYPE) -> None:
    """Cache the specified data.

    Args:
        path_cache_file: location of the cache file to write
        metadata: metadata dictionary to store in the cache file
        test_data: arbitrary test data to store

    """
    if path_cache_file.is_file():
        old_cache_dict = json.load(path_cache_file.open('r'))
        old_meta = old_cache_dict[KEY_NAME_META]
        metadata = _merge_metadata(metadata, old_meta)
        test_data = old_cache_dict[KEY_NAME_DATA]
    else:
        metadata = [metadata]

    cache_dict = {KEY_NAME_META: metadata, KEY_NAME_DATA: test_data}
    path_cache_file.parent.mkdir(exist_ok=True, parents=True)
    _json = json.dumps(cache_dict, sort_keys=True, indent=2, separators=(',', ': '), cls=CacheAssertSerializer)
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
