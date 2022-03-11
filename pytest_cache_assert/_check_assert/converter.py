"""Pytest Cache Assert Configuration Object."""

from attrs import frozen
from beartype.typing import Any, Callable, Tuple


@frozen(kw_only=True)
class Converter:
    """User-specific converters to extend the default `cache_store`."""

    types: Tuple[Any, ...]
    func: Callable[[Any], Any]
