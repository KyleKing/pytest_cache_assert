"""Utilities for managing the cache."""

from pathlib import Path

from beartype import beartype
from beartype.typing import Any, Dict, List, Optional

from .constants import CACHE_README_TEXT, KEY_NAME_DATA, KEY_NAME_META
from .error_message import NoCacheError
from .serializer import dumps, loads, make_diffable, pretty_dumps


@beartype
def init_cache(path_cache_dir: Path) -> None:
    """Ensure that the cache directory exists and add the README.

    Args:
        path_cache_dir: location of the cache directory

    """
    path_cache_dir.mkdir(exist_ok=True, parents=True)
    (path_cache_dir / 'README.md').write_text(CACHE_README_TEXT)


@beartype
def _merge_metadata(new_metadata: Dict, cached_meta_list: List[Dict]) -> List[Dict]:  # type: ignore[type-arg]
    """Merge metadata for caching. Filter duplicates.

    Args:
        new_metadata: metadata dictionary to store in the cache file
        cached_meta_list: list of old metadata dictionaries to merging

    Returns:
        List[dict]: merged metadata

    """
    all_meta = [new_metadata, *cached_meta_list]
    unique_meta = {dumps(_m, sort_keys=True) for _m in all_meta}
    return [*map(loads, sorted(unique_meta))]


@beartype
def _read_full_cache(path_cache_file: Path) -> Any:
    """Read from the cache file.

    Args:
        path_cache_file: location of the cache file to write

    Returns:
        Any: full cache dictionary including metadata

    """
    return loads(path_cache_file.read_text())


@beartype
def write_cache_data(
    path_cache_file: Path,
    *,
    metadata: Optional[Dict],  # type: ignore[type-arg]
    test_data: Any,
    always_write: bool = False,
) -> None:
    """Cache the specified data.

    Args:
        path_cache_file: location of the cache file to write
        metadata: optional dictionary for storing in the cache file
        test_data: arbitrary test data to store
        always_write: if True, overwrite the cached data

    """
    metadata = make_diffable(metadata or {})
    meta = []
    if path_cache_file.is_file():
        old_cache_dict = _read_full_cache(path_cache_file)
        old_meta = old_cache_dict[KEY_NAME_META]
        meta = _merge_metadata(metadata or {}, old_meta)
        if not always_write:  # Only change test_data if `always_write`
            test_data = old_cache_dict[KEY_NAME_DATA]

    cache_dict = {KEY_NAME_META: meta, KEY_NAME_DATA: test_data}
    path_cache_file.parent.mkdir(exist_ok=True, parents=True)
    path_cache_file.write_text(pretty_dumps(cache_dict))


@beartype
def load_cached_data(path_cache_file: Path) -> Any:
    """Cache the specified data.

    Args:
        path_cache_file: location of the cache file to write

    Returns:
        Any: loaded data from cache file

    """
    if path_cache_file.is_file():
        return _read_full_cache(path_cache_file)[KEY_NAME_DATA]
    raise NoCacheError(f'No cache for: {path_cache_file}')
