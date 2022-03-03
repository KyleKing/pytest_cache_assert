"""Pytest Plugin."""

import inspect
from functools import partial
from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest
from attrs import field, frozen
from attrs_strict import type_validator
from beartype import beartype
from beartype.typing import Any, Callable, List, Optional, Tuple

from . import main
from ._check_assert.config import CacheAssertContainerKeys, cache_assert_container
from ._check_assert.constants import DEF_CACHE_DIR_NAME
from ._check_assert.serializer import recursive_serialize


@frozen(kw_only=True)
class AssertConfig:
    """User configuration data structure."""

    cache_dir_rel_path: str = field(default=DEF_CACHE_DIR_NAME, validator=type_validator())
    """String relative directory to `tests/`. Default resolves to `tests/assert-cache/`."""

    extra_ser_rules: List[Tuple[Any, Any]] = field(factory=list, validator=type_validator())
    """Additional serialization rules. Example: `[(Enum, lambda _e: _e.name), (doit.tools.Interactive, str)]`.

    Note that lists and dictionary types are already recursively processed

    """

    always_write: bool = field(default=False, validator=type_validator())  # FIXME: TBD!
    """TBD print out warning if set to True"""

    def __attrs_post_init__(self) -> None:
        """Register relevant configuration options."""
        cache_assert_container.register(CacheAssertContainerKeys.SER_RULES, instance=self.extra_ser_rules)


@pytest.fixture()
def cache_assert_config() -> AssertConfig:
    """Configure pytest_cache_assert using `AssertConfig`."""
    return AssertConfig()


@beartype
def _calculate_metadata(request: FixtureRequest, rel_test_file: Path) -> dict:
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
    func_args = {key: recursive_serialize(value) for key, value in raw_args.items()}
    return {'test_file': rel_test_file.as_posix(), 'test_name': test_name, 'func_args': func_args}


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
    metadata = _calculate_metadata(request, rel_test_file)

    # FYI: The partial function keyword arguments can be overridden when called
    return partial(main.assert_against_cache, path_cache_dir=path_cache_dir, cache_name=cache_name, metadata=metadata)
