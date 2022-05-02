"""Pytest Cache Assert Configuration Object."""

from attrs import field, frozen
from attrs_strict import type_validator
from beartype.typing import Any, Callable, List


@frozen(kw_only=True)
class Converter:
    """User-specific converters to extend the default `cache_store`."""

    types: List[Any] = field(validator=type_validator())
    func: Callable[[Any], Any] = field(validator=type_validator())
