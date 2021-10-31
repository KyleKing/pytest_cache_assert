"""Assertion checks for unit tests.

FYI: Should not require any pytest functionality

"""

from pathlib import Path
from typing import Callable, List, Optional

from beartype import beartype

from ._check_assert import differ, error_message
from ._check_assert.caching import cache_data, init_cache, load_cached_data
from ._check_assert.constants import TEST_DATA_TYPE
from ._check_assert.key_rules import KeyRule


@beartype
def assert_against_cache(
    test_data: TEST_DATA_TYPE,
    path_cache_dir: Path,
    cache_name: str,
    key_rules: Optional[List[KeyRule]] = None,
    validator: Optional[Callable[[TEST_DATA_TYPE], None]] = None,
    metadata: Optional[dict] = None,
) -> None:
    """Core logic for pytest_cache_assert to handle caching and assertion-checking.

    Args:
        test_data: dictionary to test and/or cache
        path_cache_dir: location of the cache directory
        cache_name: relative string path from the test_dir to the JSON cache file
        key_rules: dictionary of KeyRules too apply for selectively ignoring values
        validator: Custom validation function to be run against the test data before any modification
        metadata: metadata dictionary to store in the cache file

    Raises:
        AssertionError if any assertion fails

    """
    validator = validator or (lambda _res: None)
    validator(test_data)

    path_cache_file = path_cache_dir / cache_name
    if not path_cache_dir.is_dir():
        init_cache(path_cache_dir)
    # TODO: Always write metadata. Edge case is if multiple tests use the same cache file
    #   Will merge the metadata to show values as sets
    if not path_cache_file.is_file():
        cache_data(path_cache_file, metadata or {}, test_data)
    cached_data = load_cached_data(path_cache_file)

    dict_diff = differ.diff_with_rules(old_dict=cached_data, new_dict=test_data, key_rules=key_rules or [])
    if dict_diff:
        raise AssertionError(
            error_message.create(
                test_data=test_data, cached_data=cached_data, path_cache_file=path_cache_file, dict_diff=dict_diff,
            ),
        )
