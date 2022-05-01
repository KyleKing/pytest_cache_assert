"""Implement a serializer for caching data to and from version controlled files."""

import json
import re
from pathlib import Path, PurePath

from beartype import beartype
from beartype.typing import Any, Callable, List, Pattern
from boto3.resources.base import ServiceResource
from preconvert import register
from preconvert.exceptions import Unconvertable
from preconvert.output import json as pjson

from .constants import DIFF_TYPES
from .converter import Converter

_RE_MEMORY_ADDRESS = re.compile(r' at 0x[^>]+>')
"""Regex for matching the hex memory address in a function signature."""


@beartype
def replace_memory_address(obj: Any) -> str:
    # Remove hex memory address from partial function signature
    return _RE_MEMORY_ADDRESS.sub('(..)>', str(obj))  # noqa: PD005


@register.converter(Callable)
def _replace_callable_memory_address(obj: Any) -> Any:
    return replace_memory_address(obj)


# FIXME: Support multiple levels of registered converters
@register.converter((ServiceResource, object))  # , override=True)
def _generic_memory_address_serializer(obj: Any) -> Any:
    if _RE_MEMORY_ADDRESS.search(str(obj)):
        return replace_memory_address(obj)
    raise Unconvertable(obj)


@register.converter(Path, PurePath)
def _to_path_path(obj: Path) -> str:
    return obj.as_posix()


@register.converter(Pattern)
def _to_string(obj: Any) -> str:
    return str(obj)


@register.converter(complex)
def _serialize_complex(obj: complex) -> List[float]:
    return [obj.real, obj.imag]


@beartype
def register_user_converters(converters: List[Converter]) -> None:
    """Register the user-specified converters with preconvert."""
    for converter in converters:
        register.converter(converter.types, override=True)(converter.func)


def dumps(obj: Any, sort_keys: bool = False, indent: int = 0) -> str:
    """Serialize object to str.

    Args:
        obj: data to serialize
        sort_keys: if True, order keys before serializing
        indent: indent for pretty-printing. Default is no extra whitespace

    Returns:
        str: serialized data

    Raises:
        ValueError: when serialization fails

    """
    try:
        return pjson.dumps(obj, sort_keys=sort_keys, indent=indent or None)
    except Unconvertable as exc:
        raise ValueError(f'Conversion error. Try registering a new handler with AssertConfig to fix: {exc}') from exc


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
