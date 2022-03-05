"""Pytest Plugin."""

from __future__ import annotations

import warnings
import inspect
from functools import partial
from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest
from attrs import field, frozen
from attrs_strict import type_validator
from beartype import beartype
from beartype.typing import Any, Callable, Dict, Optional

from . import main
from .cache_rel_path_resolver import CacheRelPathResolverType, CacheRelPath
from .serializer import SerializerType, JSONCacheSerializer
from .validator import ValidatorType, DiffValidator
from ._check_assert.config import CacheAssertContainerKeys, register
from ._check_assert.constants import DEF_CACHE_DIR_NAME
from ._check_assert.serializer import recursive_serialize


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


@pytest.fixture()
@beartype
def cache_assert_config() -> AssertConfig:
    """Configure pytest_cache_assert using `AssertConfig`."""
    return AssertConfig()


@beartype
def calculate_metadata(request: FixtureRequest, rel_test_file: Path) -> Dict:
    """Calculate metadata.

    Args:
        request: pytest fixture used to identify the test directory
        rel_test_file: relative path to the test file

    Returns:
        dict: new_metadata

    """
    test_name = (f'{request.cls.__name__}/' if request.cls else '') + request.node.originalname
    test_params = [*inspect.signature(request.node.function).parameters.keys()]
    raw_args = {key: value for key, value in request.node.funcargs.items() if key in test_params}
    func_args = recursive_serialize(raw_args)
    return {'test_file': rel_test_file.as_posix(), 'test_name': test_name, 'func_args': func_args}


@frozen(kw_only=True)
class TestMetadata:
    """Test MetaData."""

    test_file: str = field(validator=type_validator())
    test_name: str = field(validator=type_validator())
    func_args: Dict = field(validator=type_validator())

    @classmethod
    @beartype
    def from_pytest(cls: TestMetadata, request: FixtureRequest, rel_test_file: Path) -> TestMetadata:
        return cls(**calculate_metadata(request=request, rel_test_file=rel_test_file))


@pytest.fixture()
@beartype
def assert_against_cache(
    request: FixtureRequest,
    cache_assert_config: Optional[AssertConfig],
) -> Callable[[Any], None]:
    """Return main.assert_against_cache with pytest-specific arguments already specified.

    Args:
        request: pytest fixture used to identify the test directory
        cache_assert_config: pytest fixture that returns AssertConfig for user configuration

    Returns:
        Callable[[Any], None]: `main.assert_against_cache()` with test_dir already specified

    Raises:
        RuntimeError: if the test directory cannot be determined

    """
    cache_assert_config = cache_assert_config or AssertConfig()

    test_dir = None
    for sub_dir in ['tests', 'test']:
        test_dir = request.config.rootpath / sub_dir
        if test_dir.is_dir():
            break
    else:
        raise RuntimeError(f'Could not locate a "tests/" directory in {test_dir}')

    # Read user settings
    path_cache_dir = test_dir / cache_assert_config.cache_dir_rel_path

    # Calculate keyword arguments
    rel_test_file = Path(request.node.fspath).relative_to(test_dir)
    cache_name = (rel_test_file.parent / f'{request.node.name}.json').as_posix()  # noqa: ECE001
    metadata = TestMetadata.from_pytest(request=request, rel_test_file=rel_test_file)

    # FYI: The partial function keyword arguments can be overridden when called
    return partial(main.assert_against_cache, path_cache_dir=path_cache_dir, cache_name=cache_name, metadata=metadata)
