"""Override the default validator for determining differences with the cached data."""

from pathlib import Path

from beartype import beartype
from beartype.typing import Any, Callable, Generator, List, Optional, Protocol
from implements import Interface, implements

from .assert_rules import AssertRule
from .differ import diff_with_rules
from .error_message import RichAssertionError

try:
    from typing import Self, runtime_checkable  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Self, runtime_checkable


class Validator(Interface):  # type: ignore[misc]
    """Validator Interface."""

    @staticmethod
    def assertion(
        *, test_data: Any, cached_data: Any, assert_rules: List[AssertRule], path_cache_file: Optional[Path],
    ) -> None:
        ...


@runtime_checkable
class ValidatorType(Protocol):
    """FYI: This is a workaround for typing. See: https://github.com/ksindi/implements/issues/28"""

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], Any], None, None]:  # For Pydantic
        yield cls.validate

    @classmethod
    def validate(cls, value: Self) -> Self:
        @beartype
        def beartyper(val: Self) -> Self:
            return val

        return beartyper(value)


@implements(Validator)
class DictDiffValidator(ValidatorType):
    """Default Validator."""

    @staticmethod
    @beartype
    def assertion(
        *, test_data: Any, cached_data: Any, assert_rules: List[AssertRule], path_cache_file: Optional[Path],
    ) -> None:
        """Validate test data against cached data.

        Args:
            test_data: data to compare
            cached_data: data to compare
            assert_rules: list of assert rules to apply

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
