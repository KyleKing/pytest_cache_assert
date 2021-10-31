"""Key Rules."""

from typing import Callable

import attr

from .constants import _DIFF_TYPES


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class KeyRule:  # noqa: H601

    callable: Callable[[_DIFF_TYPES], bool]
    name: str
