"""Pytest Plugin."""

import inspect
from functools import partial
from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest
from beartype import beartype
from beartype.typing import Any, Callable, Dict

from . import main
from ._check_assert.constants import DEF_CACHE_DIR_KEY, DEF_CACHE_DIR_NAME
from ._check_assert.serializer import recursive_serialize


@pytest.fixture()
def cache_assert_config() -> Dict[str, Any]:
    """Specify a custom cache directory."""
    return {}  # noqa: DAR201


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
    cache_assert_config: Dict[str, Any],
) -> Callable[[Any], None]:
    """Yield main.assert_against_cache with pytest-specific arguments already specified.

    Args:
        request: pytest fixture used to identify the test directory
        cache_assert_config: optional pytest fixture for custom user configuration

    Returns:
        Callable[[Any], None]: `main.assert_against_cache()` with test_dir already specified

    Raises:
        RuntimeError: if the test directory cannot be determined

    """
    cache_assert_config = cache_assert_config or {}

    for sub_dir in ['tests', 'test']:
        test_dir = request.config.rootpath / sub_dir
        if test_dir.is_dir():
            break
    else:
        raise RuntimeError(f'Could not locate a "tests/" directory in {test_dir}')

    # Read user settings
    rel_dir = cache_assert_config.get(DEF_CACHE_DIR_KEY, DEF_CACHE_DIR_NAME)
    path_cache_dir = test_dir / rel_dir

    # Calculate keyword arguments
    rel_test_file = Path(request.node.fspath).relative_to(test_dir)
    cache_name = (rel_test_file.parent / f'{request.node.name}.json').as_posix()  # noqa: ECE001
    metadata = _calculate_metadata(request, rel_test_file)

    # FYI: The partial function keyword arguments can be overridden when called
    return partial(main.assert_against_cache, path_cache_dir=path_cache_dir, cache_name=cache_name, metadata=metadata)
