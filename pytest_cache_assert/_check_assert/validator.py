"""Override the default validator for determining differences with the cached data."""

from pathlib import Path
from typing import runtime_checkable

from beartype import beartype
from beartype.typing import Any, List, Optional, Protocol

from .assert_rules import AssertRule
from .differ import diff_with_rules
from .error_message import RichAssertionError


@runtime_checkable
class ValidatorType(Protocol):
    """Validator Interface."""

    @staticmethod
    def assertion(
        *, test_data: Any, cached_data: Any, assert_rules: List[AssertRule], path_cache_file: Optional[Path] = None,
    ) -> None:
        ...


class DictDiffValidator:
    """Default Validator."""

    @staticmethod
    @beartype
    def assertion(
        *, test_data: Any, cached_data: Any, assert_rules: List[AssertRule], path_cache_file: Optional[Path] = None,
    ) -> None:
        """Validate test data against cached data.

        Args:
            test_data: data to compare
            cached_data: data to compare
            assert_rules: list of assert rules to apply
            path_cache_file: optional Path to the cached data

        Raises:
            RichAssertionError: if any assertion comparison fails

        """
        diff_results = diff_with_rules(old_dict=cached_data, new_dict=test_data, assert_rules=assert_rules or [])
        if diff_results.to_dict():
            kwargs = {
                'test_data': test_data,
                'cached_data': cached_data,
                'path_cache_file': path_cache_file,
                'diff_results': diff_results,
            }
            raise RichAssertionError(RichAssertionError.create_message(**kwargs), error_info=kwargs)
