"""Representative class of the Cache Data Store."""

from pathlib import Path

from beartype import beartype
from beartype.typing import Any, Dict, Optional
from implements import Interface, implements

from .caching import init_cache, write_cache_data, load_cached_data
from .constants import TEST_DATA_TYPE
from .serializer import recursive_serialize

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


class CacheStore(Interface):

    @staticmethod
    def initialize(path_cache_dir: Path) -> None:
        ...

    @staticmethod
    def serialize(data: Any) -> TEST_DATA_TYPE:
        ...

    @staticmethod
    def write(path_cache_file: Path, *, metadata: Optional[Dict], test_data: TEST_DATA_TYPE) -> None:
        ...

    @staticmethod
    def read_cached_data(path_cache_file: Path) -> TEST_DATA_TYPE:
        ...


@runtime_checkable
class CacheStoreType(Protocol):
    """FYI: This is a workaround for typing. See: """

    ...


@implements(CacheStore)
class LocalJSONCacheStore(CacheStoreType):
    """Implementation of the CacheStore interface for a local JSON store."""

    @staticmethod
    @beartype
    def initialize(path_cache_dir: Path) -> None:
        init_cache(path_cache_dir)

    @staticmethod
    @beartype
    def serialize(data: Any) -> TEST_DATA_TYPE:
        return recursive_serialize(data=data)

    @staticmethod
    @beartype
    def write(path_cache_file: Path, *, metadata: Optional[Dict], test_data: TEST_DATA_TYPE) -> None:
        write_cache_data(path_cache_file=path_cache_file, metadata=metadata, test_data=test_data)

    @staticmethod
    @beartype
    def read_cached_data(path_cache_file: Path) -> TEST_DATA_TYPE:
        return load_cached_data(path_cache_file)
