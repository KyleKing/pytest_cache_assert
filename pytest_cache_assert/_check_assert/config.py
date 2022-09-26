"""Configuration settings."""

from enum import Enum
from uuid import uuid4

from beartype import beartype
from beartype.typing import Any, Dict
from pydantic import BaseModel, Field, PrivateAttr


class CacheAssertContainerKeys(Enum):  # noqa: H601
    """Enum of keys used in `_cache_assert_container`."""

    CONFIG = '__config__'


class MissingConfigItemError(Exception):

    ...


class _ConfigContainer(BaseModel):
    """Manage state of DoitGlobals.

    Only used for unit testing.

    """

    data: Dict[str, Any] = Field(default_factory=dict)
    _private_key_lookup: Dict[str, str] = PrivateAttr(default_factory=dict)

    @beartype
    def register(self, key: CacheAssertContainerKeys, instance: Any) -> None:
        """Registers an instance for access with `retrieve(key)`."""
        self._private_key_lookup[key.value] = self._private_key_lookup.get(key.value, str(uuid4()))
        self.data[self._private_key_lookup[key.value]] = instance

    @beartype
    def retrieve(self, key: CacheAssertContainerKeys) -> Any:
        """Retrieves the value registered for the specified key."""
        try:
            return self.data[self._private_key_lookup[key.value]]
        except KeyError:
            raise MissingConfigItemError(
                f"No '{key}' has been registered. Only: {[*self._private_key_lookup]}",
            ) from None


_cache_assert_container = _ConfigContainer()
"""Single instance."""

register = _cache_assert_container.register
retrieve = _cache_assert_container.retrieve
"""Alias for exported function."""
