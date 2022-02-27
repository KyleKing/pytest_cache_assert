"""Configuration settings."""

from enum import Enum

import punq


class CacheAssertContainerKeys(Enum):  # noqa: H601
    """Enum of keys included in `cache_assert_container`."""

    SER_RULES = 'rules'


cache_assert_container = punq.Container()
"""`punq` Container for injection of internal customization.

Currently only supports registering custom serialization rules

"""
