"""Override the default validator for determining differences with the cached data."""

from pathlib import Path

from beartype import beartype
from beartype.typing import Any, Dict, List, Optional
from implements import Interface, implements

from .differ import diff_with_rules
from .error_message import RichAssertionError
from .key_rules import KeyRule

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable

# FIXME: Need to remove this key from the Output for failed tests b/c confusing to end users
_WRAP_KEY = '--wrapped--'
"""Special key to convert lists to dictionaries for dictdiffer."""


@beartype
def _wrap_data(_data: Any) -> Any:
    """Wrap data for comparison as dictionaries.

    Args:
        _data: list or dictionary data to potentially wrap

    Returns:
        Any: wrapped data that is safe for comparison

    """
    return {_WRAP_KEY: _data} if isinstance(_data, list) else _data


'''
# FYI: Not needed because the data is already unwrapped in locals of assert_against_cache
@beartype
def _unwrap_data(_data: Any) -> Any:
    """Wrap data for comparison as dictionaries.

    Args:
        _data: safe data to potentially unwrap

    Returns:
        Any: unwrapped list or dictionary data

    """
    return _data.get(_WRAP_KEY, _data)
'''


def _safe_types(
    *, test_data: Any, cached_data: Any, key_rules: List[KeyRule],
) -> Dict:
    """Convert data and key_rules to safe data types for diffing.

    Args:
        test_data: data to compare
        cached_data: data to compare
        key_rules: list of key rules to apply

    Returns:
        Dict: safe keyword args for diff_with_rules

    """
    wrapped_key_rules = []
    for key_rule in key_rules:
        if isinstance(cached_data, list):
            key_rule.pattern = [_WRAP_KEY] + key_rule.pattern
        wrapped_key_rules.append(key_rule)

    return {
        'old_dict': _wrap_data(cached_data),
        'new_dict': _wrap_data(test_data),
        'key_rules': wrapped_key_rules,
    }


class Validator(Interface):
    """Validator Interface."""

    @staticmethod
    def assertion(
        *, test_data: Any, cached_data: Any, key_rules: List[KeyRule], path_cache_file: Optional[Path],
    ) -> None:
        ...


@runtime_checkable
class ValidatorType(Protocol):
    ...


@implements(Validator)
class DictDiffValidator(ValidatorType):
    """Default Validator."""

    @staticmethod
    @beartype
    def assertion(
        *, test_data: Any, cached_data: Any, key_rules: List[KeyRule], path_cache_file: Optional[Path],
    ) -> None:
        """Validate test data against cached data.

        Args:
            test_data: data to compare
            cached_data: data to compare
            key_rules: list of key rules to apply

        Raises:
            RichAssertionError: if any assertion comparison fails

        """
        safe_tuple = _safe_types(cached_data=cached_data, test_data=test_data, key_rules=key_rules or [])
        diff_results = diff_with_rules(**safe_tuple)

        if diff_results:
            kwargs = {
                'test_data': test_data,
                'cached_data': cached_data,
                'path_cache_file': path_cache_file,
                'diff_results': diff_results,
            }
            raise RichAssertionError(RichAssertionError.create_message(**kwargs), error_info=kwargs)
