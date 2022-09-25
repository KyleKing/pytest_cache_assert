"""Representative class of the Cache Data Store."""

from pathlib import Path

from beartype import beartype
from beartype.typing import Any, Callable, Dict, Generator, List, Optional, Protocol
from implements import Interface, implements

from .caching import init_cache, load_cached_data, write_cache_data
from .converter import Converter
from .serializer import make_diffable, register_user_converters

try:
    from typing import Self, runtime_checkable  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Self, runtime_checkable


class CacheStore(Interface):  # type: ignore[misc]

    @staticmethod
    def initialize(path_cache_dir: Optional[Path], converters: Optional[List[Converter]] = None) -> None:
        ...

    @staticmethod
    def serialize(data: Any) -> Any:
        ...

    @staticmethod
    def write(
        path_cache_file: Path,
        *,
        metadata: Optional[Dict],  # type: ignore[type-arg]
        test_data: Any,
        always_write: bool = False,
    ) -> None:
        ...

    @staticmethod
    def read_cached_data(path_cache_file: Path) -> Any:
        ...


@runtime_checkable
class CacheStoreType(Protocol):
    """FYI: This is a workaround for typing. See: https://github.com/ksindi/implements/issues/28"""

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], Any], None, None]:  # For Pydantic
        yield cls.validate

    @classmethod
    def validate(cls, value: Self) -> Self:
        @beartype
        def beartyper(val: Self) -> Self:
            return val

        return beartyper(value)


@implements(CacheStore)
class LocalJSONCacheStore(CacheStoreType):
    """Implementation of the CacheStore interface for a local JSON store."""

    @staticmethod
    @beartype
    def initialize(path_cache_dir: Optional[Path], converters: Optional[List[Converter]] = None) -> None:
        if converters:
            register_user_converters(converters)
        if path_cache_dir:
            init_cache(path_cache_dir)

    @staticmethod
    @beartype
    def serialize(data: Any) -> Any:
        return make_diffable(data=data)

    @staticmethod
    @beartype
    def write(
        path_cache_file: Path,
        *,
        metadata: Optional[Dict],  # type: ignore[type-arg]
        test_data: Any,
        always_write: bool = False,
    ) -> None:
        write_cache_data(
            path_cache_file=path_cache_file, metadata=metadata, test_data=test_data, always_write=always_write,
        )

    @staticmethod
    @beartype
    def read_cached_data(path_cache_file: Path) -> Any:
        return load_cached_data(path_cache_file)
