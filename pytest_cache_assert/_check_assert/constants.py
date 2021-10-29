"""Constants."""

from typing import Any, Dict, List, Union

_SAFE_T = Union[str, int, float, bool, None]
"""Safe types for json serialization."""

_NESTED_DICT = Dict[_SAFE_T, Union[_SAFE_T, Dict[_SAFE_T, Union[_SAFE_T, dict]]]]  # noqa: ECE001
"""Nested dictionary type."""

_NESTED_LIST = List[Union[_NESTED_DICT, _SAFE_T, list]]  # noqa: ECE001
"""Nested list type."""

TEST_DATA_TYPE = Any  # PLANNED: Consider something like: Union[_NESTED_DICT, _NESTED_LIST]
"""Test Data Type."""

KEY_NAME_META = '_info'
"""Key for metadata."""

KEY_NAME_DATA = '_json'
"""Key for cached data."""

CACHE_README_TEXT = """# Pytest Assert Cache

This folder is automatically generated by `pytest_cache_assert`.

Files can be regenerated by deleting and allowing `pytest_cache_assert` to
recreate them when next running the test suite.
"""
"""README content for the cache directory."""
