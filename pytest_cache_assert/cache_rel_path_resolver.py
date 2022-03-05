"""Relative Path Resolver for Cached Files."""

from implements import Interface, implements

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


class CacheRelPathResolver(Interface):
    ...


@runtime_checkable
class CacheRelPathResolverType(Protocol):
    ...


@implements(CacheRelPathResolver)
class CacheRelPath(CacheRelPathResolverType):
    ...
