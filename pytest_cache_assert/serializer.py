"""Implement a serializer for caching data to and from version controlled files."""

from implements import Interface, implements

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


class Serializer(Interface):
    ...


@runtime_checkable
class SerializerType(Protocol):
    ...


@implements(Serializer)
class JSONCacheSerializer(SerializerType):
    ...
