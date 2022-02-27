"""Key Rules."""

from datetime import datetime, timedelta
from enum import Enum
from functools import partial
from uuid import UUID

import pendulum
from attrs import field, mutable
from attrs_strict import type_validator
from beartype import beartype
from beartype.typing import Callable, List, Optional, Union
from pendulum.parsing.exceptions import ParserError

from .constants import DIFF_TYPES, Wildcards


class Comparator(Enum):  # noqa: H601
    """Comparator Enum for KeyRules."""

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
    for converter in [UUID, pendulum.parse, float]:
        try:
            converter(old)
            converter(new)
            return True
        except (ValueError, ParserError, AttributeError, TypeError):
            pass

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
    new_date = pendulum.parse(new)

    # Converts datetime to pendulum to ensure consistent timezones with serialized data
    if min_date and new_date < pendulum.parse(str(min_date)):
        return False
    return not (max_date and new_date > pendulum.parse(str(max_date)))


@beartype
def gen_check_date_range(
    min_date: Optional[datetime] = None, max_date: Optional[datetime] = None,
) -> Callable[[DIFF_TYPES, DIFF_TYPES], bool]:
    """Generate a KeyRule check for date within the specified range.

    Args:
        min_date: optional minimum datetime
        max_date: optional maximum datetime

    Returns:
        Callable[[DIFF_TYPES, DIFF_TYPES], bool]: KeyRule check

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
    old_date = pendulum.parse(old)
    new_date = pendulum.parse(new)

    if comparator == Comparator.LTE:
        return (new_date - old_date) <= time_delta
    elif comparator == Comparator.GTE:
        return (new_date - old_date) >= time_delta
    return abs(new_date - old_date) <= time_delta


@beartype
def gen_check_date_proximity(
    time_delta: timedelta, comparator: Comparator = Comparator.WITHIN,
) -> Callable[[DIFF_TYPES, DIFF_TYPES], bool]:
    """Generate a KeyRule check for date within the specified range.

    Args:
        time_delta: timedelta to use for checking that the new data is
        comparator: defaults to Comparator.WITHIN. Can make directional by setting LTE or GTE

    Returns:
        Callable[[DIFF_TYPES, DIFF_TYPES], bool]: KeyRule check

    """
    return partial(_check_date_proximity, time_delta=time_delta, comparator=comparator)


@mutable(kw_only=True)
class KeyRule:  # noqa: H601
    """Key Rule."""

    pattern: List[Union[str, Wildcards]] = field(validator=type_validator())
    func: Callable[[DIFF_TYPES, DIFF_TYPES], bool] = field(default=check_exact, validator=type_validator())
