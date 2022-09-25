"""Pytest Cache Assert Configuration Object."""

from beartype.typing import Any, List
from pydantic import BaseModel

from .constants import T_CONVERTER


class Converter(BaseModel, frozen=True):
    """User-specific converters to extend the default `cache_store`."""

    types: List[Any]
    func: T_CONVERTER
