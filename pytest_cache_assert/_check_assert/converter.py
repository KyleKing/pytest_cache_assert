"""Pytest Cache Assert Configuration Object."""

from beartype.typing import Any, Callable, List
from pydantic import BaseModel


class Converter(BaseModel, frozen=True):
    """User-specific converters to extend the default `cache_store`."""

    types: List[Any]
    func: Callable[[Any], Any]
