"""Implement a serializer for caching data to and from version controlled files."""

import inspect
import json
import re
from collections import defaultdict
from contextlib import suppress
from enum import Enum
from json import JSONEncoder
from pathlib import Path, PurePath
from uuid import UUID

from beartype import beartype
from beartype.typing import Any, Callable, Dict, List, Pattern, Tuple
from pydantic import BaseModel, Field

from .constants import T_CONVERTER, T_DIFF
from .converter import Converter

_RE_MEMORY_ADDRESS = re.compile(r' at 0x[^>]+>')
"""Regex for matching the hex memory address in a function signature."""


class Unconvertable(ValueError):
    """Custom Error to indicate conversion failure."""

    ...


@beartype
def replace_memory_address(obj: Any) -> str:
    # Remove hex memory address from partial function signature
    return _RE_MEMORY_ADDRESS.sub('(..)>', str(obj))  # noqa: PD005


class _Converters(BaseModel):
    """Register converters for application."""

    converters: List[Tuple[Any, T_CONVERTER]] = Field(default_factory=list)
    converter_lookup: Dict[Any, List[T_CONVERTER]] = Field(default_factory=dict)

    @beartype
    def register(self, types: List[Any], converter: T_CONVERTER) -> None:
        self.converters.extend((typ, converter) for typ in types)
        self.converter_lookup = {}

    @beartype
    def get_lookup(self) -> Dict[Any, List[T_CONVERTER]]:
        if not self.converter_lookup:
            self.converter_lookup = defaultdict(list)
            for typ, converter in self.converters[::-1]:
                self.converter_lookup[typ].append(converter)
        return self.converter_lookup


_CONVERTERS = _Converters()


class _CacheAssertSerializer(JSONEncoder):
    """Expand serializable types beyond default encoder.

    Docs: https://docs.python.org/3/library/json.html#json.JSONEncoder

    Restored from: https://github.com/KyleKing/pytest_cache_assert/blob/bcc99d04518f08fad7af34e53b2ac8cbdbe19065/pytest_cache_assert/_check_assert/serializer.py#L76-L86

    """

    def default(self, obj: Any) -> Any:
        """Extend default encoder."""
        if isinstance(obj, (bytes)):
            return str(obj)
        if isinstance(obj, (str, bytes, list, dict)):
            return super().default(obj)
        if inspect.isclass(obj):
            return replace_memory_address(str(obj))

        converters = _CONVERTERS.get_lookup().get(type(obj))
        for converter in converters or []:
            with suppress(Unconvertable):
                return converter(obj)

        for typ, converters in _CONVERTERS.get_lookup().items():
            if isinstance(obj, typ):
                for converter in converters:
                    with suppress(Unconvertable):
                        return converter(obj)

        # Fallback for classes (i.e. `UUID`) that are of type "type" and otherwise cannot be easily registered
        with suppress(Unconvertable):
            return _generic_memory_address_serializer(obj)

        raise Unconvertable(f'Failed to encode `{obj}` ({type(obj)}) with {_CONVERTERS.get_lookup()}')


def _generic_memory_address_serializer(obj: Any) -> Any:
    if _RE_MEMORY_ADDRESS.search(str(obj)):
        return replace_memory_address(obj)
    raise Unconvertable("Not a match for 'replace_memory_address'")


_CONVERTERS.register([Callable], _generic_memory_address_serializer)


def _no_op(obj: Any) -> Any:
    return obj


_CONVERTERS.register([bool, int, float], _no_op)


def _serialize_path(obj: Path) -> str:
    """Attempt to provide a path agnostic of working directory or device."""
    cwd = Path.cwd()
    pth = obj
    with suppress(AttributeError):
        pth = obj.resolve()  # Attempt to remove ".."
    # if pth.is_relative_to(cwd):  # PLANNED: Faster to LBYL or EAFP?
    with suppress(ValueError):
        return f'--/{pth.relative_to(cwd).as_posix()}'
    with suppress(ValueError):
        return f'~/{pth.relative_to(Path.home()).as_posix()}'
    return obj.as_posix()


_CONVERTERS.register([Path, PurePath], _serialize_path)


def _serialize_enum(obj: Enum) -> str:
    try:
        return str(obj.value)
    except AttributeError as exc:
        raise Unconvertable(exc) from None


_CONVERTERS.register([Enum], _serialize_enum)

_CONVERTERS.register([Pattern, UUID], str)


def _serialize_complex(obj: complex) -> List[float]:
    return [obj.real, obj.imag]


_CONVERTERS.register([complex], _serialize_complex)

with suppress(ImportError):
    from pendulum.datetime import DateTime
    _CONVERTERS.register([DateTime], str)

with suppress(ImportError):
    from arrow import Arrow
    _CONVERTERS.register([Arrow], str)

with suppress(ImportError):
    import pandas as pd

    def _serialize_pandas(obj: pd.DataFrame) -> Dict:  # type: ignore[type-arg]
        return obj.to_dict()  # type: ignore[no-any-return]

    _CONVERTERS.register([pd.DataFrame], _serialize_pandas)

with suppress(ImportError):
    import numpy as np

    def _serialize_numpy(obj: np.ndarray) -> List:  # type: ignore[type-arg]
        return obj.tolist()  # type: ignore[no-any-return]

    _CONVERTERS.register([np.ndarray], _serialize_numpy)

with suppress(ImportError):
    from pydantic.main import BaseModel

    def _serialize_pydantic(obj: BaseModel) -> Dict:  # type: ignore[type-arg]
        return obj.to_dict()  # type: ignore[attr-defined,no-any-return]

    _CONVERTERS.register([BaseModel], _serialize_pydantic)


@beartype
def register_user_converters(converters: List[Converter]) -> None:
    """Register the user-specified converters."""
    for converter in converters:
        _CONVERTERS.register(converter.types, converter.func)  # type: ignore[arg-type]


@beartype
def dumps(obj: Any, sort_keys: bool = False, indent: int = 0) -> str:
    """Serialize object to str.

    Args:
        obj: data to serialize
        sort_keys: if True, order keys before serializing
        indent: indent for pretty-printing. Default is no extra whitespace

    Returns:
        str: serialized data

    Raises:
        Unconvertable: when serialization fails

    """
    try:
        return json.dumps(obj, sort_keys=sort_keys, indent=indent or None, cls=_CacheAssertSerializer)
    except Unconvertable as exc:
        raise Unconvertable(f'Conversion error. Try specifying new converters in AssertConfig to fix: {exc}') from exc


@beartype
def pretty_dumps(obj: Any) -> str:
    """Serialize object to a pretty-printable str.

    Args:
        obj: data to serialize

    Returns:
        str: serialized data

    """
    return dumps(obj, sort_keys=True, indent=2).strip() + '\n'


@beartype
def loads(raw: str) -> T_DIFF:
    """Deserialize arbitrary JSON data back to Python types.

    Args:
        raw: raw string JSON

    Returns:
        T_DIFF: DiffResults-safe data

    """
    return json.loads(raw)


@beartype
def make_diffable(data: Any) -> T_DIFF:
    """Convert raw object to diffable types for assertion checks.

    Args:
        data: data to serialize

    Returns:
        T_DIFF: DiffResults-safe data

    """
    return loads(dumps(data))
