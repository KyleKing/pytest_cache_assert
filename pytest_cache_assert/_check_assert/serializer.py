"""Provide additional encoding functionality to check_assert."""

import re
from json import JSONEncoder
from pathlib import Path, PurePath

import punq
from beartype import beartype
from beartype.typing import Any, Callable, Dict, Pattern, Union

from .config import CacheAssertContainerKeys, cache_assert_container

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
    rules = []
    try:
        rules = cache_assert_container.resolve(CacheAssertContainerKeys.SER_RULES)
    except punq.MissingDependencyError:
        ...
    rules.extend([
        [Callable, replace_memory_address],
        [(Path, PurePath), Path.as_posix],
        [Pattern, str],
        [complex, lambda _o: [_o.real, _o.imag]],
    ])
    for _types, func in rules:
        if isinstance(value, _types):
            return func(value)

    return value


@beartype
def recursive_serialize(value: Any) -> Union[Dict[str, Any], str]:
    """Recursive serialization function.

    Args:
        value: value to serialize

    Returns:
        Union[Dict[str, Any], str]: JSON-safe data

    """
    if isinstance(value, dict) and value:
        return {_k: recursive_serialize(_v) for _k, _v in value.items()}

    return str(coerce_if_known_type(value))


class CacheAssertSerializer(JSONEncoder):
    """Expand serializable types beyond default encoder.

    Docs: https://docs.python.org/3/library/json.html#json.JSONEncoder

    """

    def default(self, obj: Any) -> Any:
        """Extend default encoder."""
        obj = coerce_if_known_type(obj)
        return obj if isinstance(obj, str) else JSONEncoder.default(self, obj)
