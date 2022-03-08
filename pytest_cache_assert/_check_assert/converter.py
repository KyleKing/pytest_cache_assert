"""Pytest Cache Assert Configuration Object."""

from attrs import field, frozen
from attrs_strict import type_validator
from beartype.typing import Any, Callable


@frozen(kw_only=True)
class Converter:
    """User-specific converters to extend the default `cache_store`."""

    types: Any
    func: Callable[[Any], Any] = field(validator=type_validator())
