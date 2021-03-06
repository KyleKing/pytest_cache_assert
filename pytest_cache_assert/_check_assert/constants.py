"""Constants."""

from datetime import datetime
from enum import Enum

from beartype.typing import Dict, Iterable, List, Type, Union


class Wildcards(Enum):  # noqa: H601
    """Pattern Matching Wildcards."""

    SINGLE = 1
    """Replace a single dictionary key."""

    RECURSIVE = 2
    """Apply to all keys at or below this wildcard."""

    LIST = 4
    """Pseudo-key for a list containing dictionaries."""

    def __str__(self) -> str:
        """Return string representation for sorting.

        Returns:
            str: index as a string with dashes for sorting last

        """
        return f'--{self.name}--'


class TrueNull:  # noqa: H601
    """Indicate that the old or new value does not exist.

    Note: `attrs.NOTHING` is a singleton and can't be used for type annotations

    """

    ...


_SAFE_T = Union[str, int, float, bool, None]
"""Safe types for json serialization."""

_NESTED_DICT = Dict[_SAFE_T, Union[_SAFE_T, Dict[_SAFE_T, Union[_SAFE_T, dict]]]]  # noqa: ECE001
"""Nested dictionary type."""

_NESTED_LIST = List[Union[_NESTED_DICT, _SAFE_T, list]]  # noqa: ECE001
"""Nested list type."""

_DIFF_SINGLE_TYPES = Union[None, str, int, float, datetime]
"""Single types for DIFF_TYPES."""

DIFF_TYPES = Union[_DIFF_SINGLE_TYPES, Type[TrueNull], Iterable[_DIFF_SINGLE_TYPES]]
"""Possible Old or New difference type."""

DEF_CACHE_DIR_NAME = 'assert-cache'
"""Default `pytest_assert_cache` directory name."""

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
