"""Pytest Cache Assert Configuration Object."""

import warnings

from attrs import field, frozen
from attrs_strict import type_validator

from .cache_rel_path_resolver import CacheRelPath, CacheRelPathResolverType
from .config import CacheAssertContainerKeys, register
from .constants import DEF_CACHE_DIR_NAME
from .serializer import JSONCacheSerializer, SerializerType
from .validator import DiffValidator, ValidatorType


@frozen(kw_only=True)
class AssertConfig:
    """User configuration data structure."""

    cache_dir_rel_path: str = field(default=DEF_CACHE_DIR_NAME, validator=type_validator())
    """String relative directory from `tests/`. Default resolves to `tests/assert-cache/`."""

    # FIXME: This needs to be implemented
    always_write: bool = field(default=False, validator=type_validator())
    """Always write to the cached file so that diffs can be examined in the user's VCS."""

    # FIXME: This needs to be implemented
    cache_rel_path_resolver: CacheRelPathResolverType = field(factory=CacheRelPath, validator=type_validator())
    """Any class that implements the CacheRelPathResolver interface to determine the relative path.

    This is useful if you want to override the nested directory structure and file names

    """

    # FIXME: This needs to be implemented
    serializer: SerializerType = field(factory=JSONCacheSerializer, validator=type_validator())
    """Replacement serializer to replace the default JSON one.

    Override the default `serializer` to have a custom cache format

    """

    # FIXME: This needs to be implemented
    validator: ValidatorType = field(factory=DiffValidator, validator=type_validator())
    """Custom validator for identifying and summarizing the differences with cached data to StdOut."""

    def __attrs_post_init__(self) -> None:
        """Register the configuration object."""
        if self.always_write:
            warnings.warn('User has configured always_write globally. Make sure to check-in files to a VCS')
        register(CacheAssertContainerKeys.CONFIG, self)
