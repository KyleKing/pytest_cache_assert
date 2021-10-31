"""Key Rules."""

from typing import Callable, List

import attr
import pendulum
from attrs_strict import type_validator
from beartype import beartype
from pendulum.parsing.exceptions import ParserError

from .constants import DIFF_TYPES


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
def check_type(old: DIFF_TYPES, new: DIFF_TYPES) -> bool:
    """Check if both values are the exact same or same non-string type.

    Will attempt to parse strings to int, float, or datetime.

    Args:
        old: the old value
        new: the new value

    Returns:
        bool: True if both values are the same kind

    """
    if (
        check_exact(old=old, new=new)  # Catches if both null, etc.
        or (not isinstance(old, str) and type(old) == type(new))
    ):
        return True

    for converter in [int, float, pendulum.parse]:
        try:
            converter(old)
            converter(new)
            return True
        except (ValueError, ParserError):
            pass

    return False


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class KeyRule:  # noqa: H601
    """Key Rule."""

    key_list: List[str] = attr.ib(validator=type_validator())
    func: Callable[[DIFF_TYPES, DIFF_TYPES], bool] = attr.ib(default=check_exact, validator=type_validator())
