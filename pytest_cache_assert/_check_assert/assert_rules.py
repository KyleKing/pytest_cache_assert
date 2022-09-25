"""Key Rules."""

import re
from contextlib import suppress
from datetime import datetime, timedelta
from enum import Enum
from functools import partial
from typing import ClassVar
from uuid import UUID

import arrow
from beartype import beartype
from beartype.typing import Callable, List, Optional, Pattern, Union
from pydantic.dataclasses import dataclass
from strenum import StrEnum

from .constants import DIFF_TYPES


class Comparator(Enum):  # noqa: H601
    """Comparator Enum for AssertRules."""

    LTE = 'new - old <= value'
    GTE = 'new - old >= value'
    WITHIN = 'abs(new - old) <= value'


@beartype
def check_suppress(old: DIFF_TYPES, new: DIFF_TYPES) -> bool:
    """Return True to suppress differences.

    Args:
        old: the old value
        new: the new value

    Returns:
        bool: Always True

    """
    return True


@beartype
def check_exact(old: DIFF_TYPES, new: DIFF_TYPES) -> bool:
    """Check for value equality.

    Args:
        old: the old value
        new: the new value

    Returns:
        bool: True if both values are the exact same

    """
    return old == new


@beartype
def _try_type_coercion(old: DIFF_TYPES, new: DIFF_TYPES) -> bool:
    """Attempt to coerce strings to UUID, datetime, or int/float.

    Args:
        old: the old value
        new: the new value

    Returns:
        bool: True if both values are the same kind

    """
    for converter in [UUID, arrow.get, float]:
        with suppress((ValueError, AttributeError, TypeError, arrow.parser.ParserError)):
            converter(old)
            converter(new)
            return True

    return False


@beartype
def check_type(old: DIFF_TYPES, new: DIFF_TYPES) -> bool:
    """Check if both values are the exact same or same non-string type. Will attempt conversion from string.

    Args:
        old: the old value
        new: the new value

    Returns:
        bool: True if both values are the same kind

    """
    if (
        check_exact(old=old, new=new)  # Catches if both null, etc.
        or (not isinstance(old, str) and isinstance(old, type(new)))
    ):
        return True

    return _try_type_coercion(old=old, new=new)


@beartype
def _check_date_range(
    old: DIFF_TYPES, new: DIFF_TYPES,
    min_date: Optional[datetime] = None, max_date: Optional[datetime] = None,
) -> bool:
    """Check if the new date falls within the specified range. Will ignores old date.

    Args:
        old: the old value
        new: the new value
        min_date: optional minimum datetime
        max_date: optional maximum datetime

    Returns:
        bool: True if the new date is within the specified range

    """
    new_date = arrow.get(str(new))

    # Converts datetime to arrow to ensure consistent timezones with serialized data
    if min_date and new_date < arrow.get(str(min_date)):
        return False
    return not (max_date and new_date > arrow.get(str(max_date)))


@beartype
def gen_check_date_range(
    min_date: Optional[datetime] = None, max_date: Optional[datetime] = None,
) -> Callable[[DIFF_TYPES, DIFF_TYPES], bool]:
    """Generate a AssertRule check for date within the specified range.

    Args:
        min_date: optional minimum datetime
        max_date: optional maximum datetime

    Returns:
        Callable[[DIFF_TYPES, DIFF_TYPES], bool]: AssertRule check

    """
    return partial(_check_date_range, min_date=min_date, max_date=max_date)


@beartype
def _check_date_proximity(
    old: DIFF_TYPES, new: DIFF_TYPES, time_delta: timedelta, comparator: Comparator,
) -> bool:
    """Check if the new date is proximal to the old date based on a time_delta and comparison logic.

    Args:
        old: the old value
        new: the new value
        time_delta: timedelta to use for checking that the new data is
        comparator: Comparator logic to implement

    Returns:
        bool: True if the new date meets the proximity criteria of timedelta and comparator

    """
    old_date = arrow.get(str(old))
    new_date = arrow.get(str(new))

    if comparator == Comparator.LTE:
        return (new_date - old_date) <= time_delta
    elif comparator == Comparator.GTE:
        return (new_date - old_date) >= time_delta
    return abs(new_date - old_date) <= time_delta


@beartype
def gen_check_date_proximity(
    time_delta: timedelta, comparator: Comparator = Comparator.WITHIN,
) -> Callable[[DIFF_TYPES, DIFF_TYPES], bool]:
    """Generate a AssertRule check for date within the specified range.

    Args:
        time_delta: timedelta to use for checking that the new data is
        comparator: defaults to Comparator.WITHIN. Can make directional by setting LTE or GTE

    Returns:
        Callable[[DIFF_TYPES, DIFF_TYPES], bool]: AssertRule check

    """
    return partial(_check_date_proximity, time_delta=time_delta, comparator=comparator)


_PAT_JOIN = r'\]\['


class Wild(StrEnum):
    """AssertRule Wildcard Patterns."""

    @classmethod
    def index(cls, count: int = 1) -> str:
        """Return pattern that matches one or more nested lists in the cached data."""
        return _PAT_JOIN.join([r'\d+'] * count)

    @classmethod
    def keys(cls, count: int = 1) -> str:
        """Return pattern that matches one or more nested dictionary keys."""
        return _PAT_JOIN.join([r'[^\]]+'] * count)


@dataclass(kw_only=True)
class AssertRule:  # noqa: H601
    """Key Rule."""

    pattern: Union[str, Pattern]
    func: Callable[[DIFF_TYPES, DIFF_TYPES], bool]
    is_regex: ClassVar[bool]

    def __post_init__(self) -> None:
        """Register the configuration object."""
        self.is_regex = not isinstance(self.pattern, str)

    @classmethod
    def build_re(cls, pattern: List[Union[str, Wild]], func: Callable[[DIFF_TYPES, DIFF_TYPES], bool]) -> 'AssertRule':
        """Build a regex pattern from list."""
        if not pattern:
            raise ValueError("Expected at least one item in 'pattern'")
        if pattern[0].startswith('root['):
            raise ValueError("Exclude 'root' and brackets. This method builds it for you")
        pattern_re = r"root\['" + _PAT_JOIN.join(pattern) + r'\]'
        return cls(pattern=re.compile(pattern_re), func=func)
