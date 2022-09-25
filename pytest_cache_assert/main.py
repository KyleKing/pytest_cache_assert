"""Assertion checks for unit tests.

FYI: Should not require any pytest functionality

"""

from pathlib import Path

from beartype import beartype
from beartype.typing import Any, Dict, List, Optional

from . import AssertRule, CacheAssertContainerKeys, NoCacheError, retrieve


@beartype
def assert_against_dict(
    old_dict: Dict,  # type: ignore[type-arg]
    new_dict: Dict,  # type: ignore[type-arg]
    assert_rules: Optional[List[AssertRule]] = None,
) -> None:
    """Utilize custom DictDiffer logic to compare in-memory dictionaries.

    Args:
        old_dict: old dictionary (typically cached one)
        new_dict: new dictionary (typically test data)
        assert_rules: dictionary of AssertRules to apply when selectively ignoring differences

    """
    config = retrieve(CacheAssertContainerKeys.CONFIG)
    cache_store = config.cache_store
    cache_store.initialize(None, config.converters)
    new_dict = cache_store.serialize(new_dict)

    validator = config.validator
    validator.assertion(cached_data=old_dict, test_data=new_dict, assert_rules=assert_rules or [])


@beartype
def assert_against_cache(
    test_data: Any,
    *,
    path_cache_dir: Path,
    cache_name: str,
    assert_rules: Optional[List[AssertRule]] = None,
    metadata: Optional[Dict] = None,  # type: ignore[type-arg]
    always_write: Optional[bool] = None,
) -> None:
    """Core logic for pytest_cache_assert to handle caching and assertion-checking.

    Args:
        test_data: dictionary or list to test (could be from cache)
        path_cache_dir: location of the cache directory
        cache_name: relative string path from the test_dir to the JSON cache file
        assert_rules: dictionary of AssertRules to apply when selectively ignoring differences
        metadata: metadata dictionary to store in the cache file
        always_write: if True, always write the changes

    """
    config = retrieve(CacheAssertContainerKeys.CONFIG)
    cache_store = config.cache_store
    path_cache_file = path_cache_dir / cache_name
    cache_store.initialize(path_cache_dir, config.converters)
    test_data = cache_store.serialize(test_data)
    # Function argument overrides global
    aw = config.always_write if always_write is None else always_write
    try:
        cached_data = cache_store.read_cached_data(path_cache_file)
    except NoCacheError:
        cached_data = test_data
    cache_store.write(path_cache_file, metadata=metadata, test_data=test_data, always_write=aw)

    validator = config.validator
    validator.assertion(
        cached_data=cached_data, test_data=test_data, assert_rules=assert_rules or [],
        path_cache_file=path_cache_file,
    )
