"""Implement a serializer for caching data to and from version controlled files."""

import json
import re
from pathlib import Path, PurePath

from beartype import beartype
from beartype.typing import Any, Callable, List, Pattern
from preconvert import register
from preconvert.output import json as pjson

from .constants import DIFF_TYPES

_RE_MEMORY_ADDRESS = re.compile(r' at 0x[^>]+>')
"""Regex for matching the hex memory address in a function signature."""


@register.converter(Callable)
@beartype
def _replace_memory_address(obj: Callable) -> str:
    # Remove hex memory address from partial function signature
    return _RE_MEMORY_ADDRESS.sub('(..)>', str(obj))  # noqa: PD005


@register.converter(Path, PurePath)
def _to_path_path(obj: Path) -> str:
    return obj.as_posix()


@register.converter(Pattern)
def _to_string(obj: Any) -> str:
    return str(obj)


@register.converter(complex)
def _serialize_complex(obj: complex) -> List[float]:
    return [obj.real, obj.imag]


def dumps(obj: Any, sort_keys: bool = False, indent: int = 0) -> str:
    """Serialize object to str.

    Args:
        obj: data to serialize
        sort_keys: if True, order keys before serializing
        indent: indent for pretty-printing. Default is no extra whitespace

    Returns:
        str: serialized data

    """
    return pjson.dumps(obj, sort_keys=sort_keys, indent=indent or None)


def pretty_dumps(obj: Any) -> str:
    """Serialize object to a pretty-printable str.

    Args:
        obj: data to serialize

    Returns:
        str: serialized data

    """
    return dumps(obj, sort_keys=True, indent=2).strip() + '\n'


def loads(raw: str) -> DIFF_TYPES:
    """Deserialize arbitrary JSON data back to Python types.

    Args:
        raw: raw string JSON

    Returns:
        DIFF_TYPES: DiffResult-safe data

    """
    return json.loads(raw)


def make_diffable(data: Any) -> DIFF_TYPES:
    """Convert raw object to diffable types for assertion checks.

    Args:
        data: data to serialize

    Returns:
        DIFF_TYPES: DiffResult-safe data

    """
    # TODO: Use JSONEncoder directly
    return loads(dumps(data))
