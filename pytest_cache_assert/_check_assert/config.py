"""Configuration settings."""

from enum import Enum

import punq
from beartype import beartype
from beartype.typing import Any


class CacheAssertContainerKeys(Enum):  # noqa: H601
    """Enum of keys used in `cache_assert_container`."""

    CONFIG = '__config__'


cache_assert_container = punq.Container()
"""`punq` Container for injection of internal customization.

Currently only supports registering custom serialization rules

"""


@beartype
def register(key: CacheAssertContainerKeys, instance: Any) -> None:
    """Registers an instance for access with `retrieve(key)`."""
    cache_assert_container.register(key, instance=instance)


@beartype
def retrieve(key: CacheAssertContainerKeys) -> Any:
    """Retrieves the value registered for the specified key."""
    return cache_assert_container.resolve(key)
