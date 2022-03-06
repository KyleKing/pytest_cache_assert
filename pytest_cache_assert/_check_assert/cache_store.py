"""Representative class of the Cache Data Store."""

from beartype import beartype
from implements import Interface, implements

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


class CacheStore(Interface):

    def create(self, TBD) -> None:
        ...


@runtime_checkable
class CacheStoreType(Protocol):
    ...


@implements(CacheStore)
class LocalJSONCacheStore(CacheStoreType):
    """Implementation of the CacheStore interface for a local JSON store."""

    # TODO: Methods for init/read/write. Uses `caching.py` internally

    @beartype
    def create(self, TBD) -> None:
        ...

