"""Pytest Plugin."""

import inspect
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import pytest
from _pytest.fixtures import FixtureRequest
from beartype import beartype

from . import main
from ._check_assert.constants import DEF_CACHE_DIR_KEY, DEF_CACHE_DIR_NAME

# PLANNED: Provide CLI args return request.config.getoption("--record-mode") or "none"
# https://github.com/kiwicom/pytest-recording/blob/484bb887dd43fcaf44149160d57b58a7215e2c8a/src/pytest_recording/plugin.py#L37-L70


@pytest.fixture()
@beartype
def assert_against_cache(request: FixtureRequest, cache_assert_config: Optional[Dict[str, Any]]) -> Callable[[Any], None]:
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

    test_name = (f'{request.cls.__name__}/' if request.cls else '') + request.node.originalname
    test_file = Path(request.node.fspath)
    cache_name = (test_file.parent.relative_to(test_dir) / f'{request.node.name}.json').as_posix()  # noqa: ECE001
    # Read user setting
    rel_dir = cache_assert_config.get(DEF_CACHE_DIR_KEY, DEF_CACHE_DIR_NAME)
    path_cache_dir = test_dir / rel_dir

    # PLANNED: serialize the func_args metadata recursively
    test_params = [*inspect.signature(request.node.function).parameters.keys()]
    func_args = {key: str(value) for key, value in request.node.funcargs.items() if key in test_params}
    metadata = {'test_file': test_file.as_posix(), 'test_name': test_name, 'func_args': func_args}

    # FYI: The keyword arguments can be overridden by the test function
    return partial(main.assert_against_cache, path_cache_dir=path_cache_dir, cache_name=cache_name, metadata=metadata)
