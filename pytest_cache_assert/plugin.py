"""Pytest Plugin."""

import inspect
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

import pytest
from _pytest.fixtures import FixtureRequest
from beartype import beartype

from . import main
from ._check_assert.constants import DEF_CACHE_DIR_KEY, DEF_CACHE_DIR_NAME


@beartype
def _serialize(key: str, value: Any) -> Union[dict, str]:
    """Recursive serialization function.

    Args:
        key: string key name
        value: value to serialize

    Returns:
        Union[dict, str]: JSON-safe data

    """
    return {key: _serialize(key, value) if isinstance(value, dict) else str(value)}


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
    func_args = {}
    for key, value in raw_args.items():
        func_args.update(_serialize(key, value))
    return {'test_file': rel_test_file.as_posix(), 'test_name': test_name, 'func_args': func_args}


@pytest.fixture()
@beartype
def assert_against_cache(request: FixtureRequest,
                         cache_assert_config: Optional[Dict[str, Any]]) -> Callable[[Any], None]:
    """Yield main.assert_against_cache with pytest-specific arguments already specified.

    Args:
        request: pytest fixture used to identify the test directory
        cache_assert_config: pytest fixture for custom user configuration

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
