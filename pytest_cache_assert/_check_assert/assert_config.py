"""Pytest Cache Assert Configuration Object."""


from beartype.typing import List
from pydantic import BaseModel, Field

from .cache_store import CacheStoreType, LocalJSONCacheStore
from .config import CacheAssertContainerKeys, MissingConfigItemError, register, retrieve
from .constants import DEF_CACHE_DIR_NAME
from .converter import Converter
from .validator import DictDiffValidator, ValidatorType


class AssertConfig(BaseModel):
    """User configuration data structure."""

    always_write: bool = False
    """Always write to the cached file so that diffs can be examined in the user's VCS."""

    cache_dir_rel_path: str = DEF_CACHE_DIR_NAME
    """String relative directory from `tests/`. Default resolves to `tests/assert-cache/`."""

    cache_store: CacheStoreType = Field(default_factory=LocalJSONCacheStore)
    """Configurable class for managing the cache representation. Default is local JSON.

    Override the default `cache_store` to have a custom cache format and serialization

    """

    converters: List[Converter] = Field(default_factory=list)
    """Extend cache_store with custom functions for serializing novel types.

    Example: `[Converter(types=[pd.DataFrame], func=panda_to_json)]` for

    ```py
    def panda_to_json(df: pd.DataFrame) -> List[Dict]:
        return json.loads(df.to_json(orient='records'))
    ```

    Useful for serializing data form pandas or other types that are unknown to the generic converters

    """

    validator: ValidatorType = Field(default_factory=DictDiffValidator)
    """Custom validator for identifying and summarizing the deviations from the cache."""

    class Config:
        arbitrary_types_allowed = True


# Ensure that a default AssertConfig is always registered
try:
    retrieve(CacheAssertContainerKeys.CONFIG)
except MissingConfigItemError:
    register(CacheAssertContainerKeys.CONFIG, AssertConfig())
