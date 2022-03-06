"""Pytest Cache Assert Configuration Object."""

import warnings

import punq
from attrs import field, frozen
from attrs_strict import type_validator

from .cache_store import CacheStoreType, LocalJSONCacheStore
from .config import CacheAssertContainerKeys, register, retrieve
from .constants import DEF_CACHE_DIR_NAME
from .validator import DiffValidator, ValidatorType


@frozen(kw_only=True)
class AssertConfig:
    """User configuration data structure."""

    # FIXME: This needs to be implemented
    always_write: bool = field(default=False, validator=type_validator())
    """Always write to the cached file so that diffs can be examined in the user's VCS."""

    cache_dir_rel_path: str = field(default=DEF_CACHE_DIR_NAME, validator=type_validator())
    """String relative directory from `tests/`. Default resolves to `tests/assert-cache/`."""

    cache_store: CacheStoreType = field(factory=LocalJSONCacheStore, validator=type_validator())
    """Configurable class for managing the cache representation. Default is local JSON.

    Override the default `cache_store` to have a custom cache format and serialization

    """

    # FIXME: This needs to be implemented
    validator: ValidatorType = field(factory=DiffValidator, validator=type_validator())
    """Custom validator for identifying and summarizing the deviations from the cache."""

    def __attrs_post_init__(self) -> None:
        """Register the configuration object."""
        if self.always_write:
            warnings.warn('User has configured always_write globally. Make sure to check-in files to a VCS')
        register(CacheAssertContainerKeys.CONFIG, self)


# Ensure that a default AssertConfig is always registered
try:
    retrieve(CacheAssertContainerKeys.CONFIG)
except punq.MissingDependencyError:
    register(CacheAssertContainerKeys.CONFIG, AssertConfig())
