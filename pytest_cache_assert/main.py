"""Assertion checks for unit tests.

FYI: Should not require any pytest functionality

"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from beartype import beartype

from ._check_assert import differ, error_message
from ._check_assert.caching import init_cache, load_cached_data, write_cache_data
from ._check_assert.constants import TEST_DATA_TYPE
from ._check_assert.error_message import RichAssertionError
from ._check_assert.key_rules import KeyRule

_WRAP_KEY = '--wrapped--'
"""Special key to convert lists to dictionaries for dictdiffer."""


@beartype
def _wrap_data(_data: Any) -> TEST_DATA_TYPE:
    """Wrap data for comparison as dictionaries.

    Args:
        _data: list or dictionary data to potentially wrap

    Returns:
        TEST_DATA_TYPE: wrapped data that is safe for comparison

    """
    return {_WRAP_KEY: _data} if isinstance(_data, list) else _data


'''
# FYI: Not needed because the data is already unwrapped in locals of assert_against_cache
@beartype
def _unwrap_data(_data: TEST_DATA_TYPE) -> Any:
    """Wrap data for comparison as dictionaries.

    Args:
        _data: safe data to potentially unwrap

    Returns:
        Any: unwrapped list or dictionary data

    """
    return _data.get(_WRAP_KEY, _data)
'''


def _safe_types(
    test_data: Any, cached_data: Any, key_rules: List[KeyRule],
) -> Dict[str, Union[TEST_DATA_TYPE, List[KeyRule]]]:
    """Convert data and key_rules to safe data types for diffing.

    Args:
        test_data: data to compare
        cached_data: data to compare
        key_rules: list of key rules to apply

    Returns:
        Dict[str, Union[TEST_DATA_TYPE, List[KeyRule]]]: safe keyword args for diff_with_rules

    """
    wrapped_key_rules = []
    for key_rule in key_rules:
        if isinstance(cached_data, list):
            key_rule.pattern = [_WRAP_KEY] + key_rule.pattern
        wrapped_key_rules.append(key_rule)

    return {
        'old_dict': _wrap_data(test_data),
        'new_dict': _wrap_data(cached_data),
        'key_rules': wrapped_key_rules,
    }


@ beartype
def assert_against_cache(
    test_data: Any,
    path_cache_dir: Path,
    cache_name: str,
    key_rules: Optional[List[KeyRule]] = None,
    validator: Optional[Callable[[TEST_DATA_TYPE], None]] = None,
    metadata: Optional[dict] = None,
) -> None:
    """Core logic for pytest_cache_assert to handle caching and assertion-checking.

    Args:
        test_data: dictionary or list to test (could be from cache)
        path_cache_dir: location of the cache directory
        cache_name: relative string path from the test_dir to the JSON cache file
        key_rules: dictionary of KeyRules too apply for selectively ignoring values
        validator: Custom validation function to be run against the test data before any modification
        metadata: metadata dictionary to store in the cache file

    Raises:
        RichAssertionError: if any assertion fails

    """
    validator = validator or (lambda _res: None)
    validator(test_data)

    path_cache_file = path_cache_dir / cache_name
    if not path_cache_dir.is_dir():
        init_cache(path_cache_dir)
    write_cache_data(path_cache_file, metadata or {}, test_data)
    cached_data = load_cached_data(path_cache_file)

    dict_diff = differ.diff_with_rules(**_safe_types(test_data, cached_data, key_rules or []))
    if dict_diff:
        kwargs = {
            'test_data': test_data,
            'cached_data': cached_data,
            'path_cache_file': path_cache_file,
            'dict_diff': dict_diff,
        }
        raise RichAssertionError(error_message.create(**kwargs), error_info=kwargs)
