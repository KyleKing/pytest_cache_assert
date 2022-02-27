"""Provide additional encoding functionality to check_assert."""

import inspect
import re
from functools import partial
from json import JSONEncoder
from pathlib import Path, PurePath

from beartype import beartype
from beartype.typing import Any, Dict, Union

_RE_MEMORY_ADDRESS = re.compile(r' at 0x[^>]+>')
"""Regex for matching the hex memory address in a function signature."""


@beartype
def coerce_if_known_type(value: Any) -> Any:
    """Coerce value to standard primitive if known.

    Args:
        value: value to serialize

    Returns:
        Any: possibly unmodified data

    """
    if inspect.isfunction(value) or isinstance(value, partial):
        # Remove hex memory address from partial function signature
        return _RE_MEMORY_ADDRESS.sub('(..)>', str(value))  # noqa: PD005

    if isinstance(value, (Path, PurePath)):
        return value.as_posix()

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
        encodable_types = {
            complex: lambda _o: [_o.real, _o.imag],
        }
        for _type, converter in encodable_types.items():
            if isinstance(obj, _type):
                return converter(obj)
        obj = coerce_if_known_type(obj)

        return obj if isinstance(obj, str) else JSONEncoder.default(self, obj)
