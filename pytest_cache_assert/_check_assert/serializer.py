"""Implement a serializer for caching data to and from version controlled files."""

import re
from datetime import datetime
from enum import Enum
from json import JSONEncoder
from pathlib import Path, PurePath
from uuid import UUID

from beartype import beartype
from beartype.typing import Any, Callable, Dict, Iterable, List, Pattern

from .constants import DIFF_TYPES

_RE_MEMORY_ADDRESS = re.compile(r' at 0x[^>]+>')
"""Regex for matching the hex memory address in a function signature."""


@beartype
def replace_memory_address(obj: Callable) -> str:
    # Remove hex memory address from partial function signature
    return _RE_MEMORY_ADDRESS.sub('(..)>', str(obj))  # noqa: PD005


@beartype
def coerce_if_known_type(value: Any) -> Any:
    """Coerce value to standard primitive if known.

    Args:
        value: value to serialize

    Returns:
        Any: possibly unmodified data

    """
    rules = [
        ((Path, PurePath), Path.as_posix),
        (Callable, replace_memory_address),
        (Enum, lambda _e: _e.value),
        ((datetime, UUID, Pattern), str),
        (complex, lambda _o: [_o.real, _o.imag]),
    ]
    for _types, func in rules:
        if isinstance(value, _types):
            return func(value)

    # Handle generic classes not recognized by inspect.isclass()
    if value and not isinstance(value, (Dict, Iterable, int, float)) and str(type(value)).startswith('<class'):
        return str(value)

    return value


@beartype
def recursive_serialize(data: Any) -> DIFF_TYPES:
    """Recursive serialization of arbitrary data.

    Args:
        data: data to serialize

    Returns:
        DIFF_TYPES: DiffResult-safe data

    """
    data = coerce_if_known_type(data)

    if isinstance(data, (tuple, List)):
        return [*map(coerce_if_known_type, data)]  # For performance, only provides one level of recursion
    if isinstance(data, dict) and data:
        return {_k: recursive_serialize(_v) for _k, _v in data.items()}

    return data



class CacheAssertSerializer(JSONEncoder):
    """Expand serializable types beyond default encoder.

    Docs: https://docs.python.org/3/library/json.html#json.JSONEncoder

    """

    def default(self, obj: Any) -> Any:
        """Extend default encoder."""
        obj = coerce_if_known_type(obj)
        return obj if isinstance(obj, str) else JSONEncoder.default(self, obj)
