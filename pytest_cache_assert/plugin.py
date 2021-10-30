"""Pytest Plugin."""

import inspect
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict

import pytest
from _pytest.fixtures import FixtureRequest
from beartype import beartype

from . import checks
from ._check_assert.caching import resolve_cache_name
from ._check_assert.constants import DEF_CACHE_DIR_NAME

# PLANNED: Provide CLI args return request.config.getoption("--record-mode") or "none"
# https://github.com/kiwicom/pytest-recording/blob/484bb887dd43fcaf44149160d57b58a7215e2c8a/src/pytest_recording/plugin.py#L37-L70


@pytest.fixture(scope='session')
def check_assert_parameter_counter() -> Dict[str, int]:
    """Track the times each specific test function has been run.

    Returns:
        Dict[str, int]: dictionary to count repetitions of a key

    """
    # PLANNED: Should be a class, but a dictionary is fine for now
    counter: Dict[str, int] = {}
    return counter


@pytest.fixture()
@beartype
def assert_against_cache(
    request: FixtureRequest,
    check_assert_parameter_counter: Dict[str, int],
) -> Callable[[Any], None]:
    """Yield checks.assert_against_cache with pytest-specific arguments already specified.

    Args:
        request: pytest fixture used to identify the test directory
        check_assert_parameter_counter: pytest fixture used to track the current parameter index

    Returns:
        Callable[[Any], None]: `checks.assert_against_cache()` with test_dir already specified

    Raises:
        RuntimeError: if the test directory cannot be determined

    """
    for sub_dir in ['tests', 'test']:
        test_dir = request.config.rootpath / sub_dir
        if test_dir.is_dir():
            break
    else:
        raise RuntimeError(f'Could not locate a "tests/" directory in {test_dir}')

    test_name = (f'{request.cls.__name__}/' if request.cls else '') + request.node.originalname

    test_file = Path(request.node.fspath)
    parameter_index = check_assert_parameter_counter.get(test_name, 0)
    check_assert_parameter_counter[test_name] = parameter_index + 1
    cache_name = resolve_cache_name(test_dir, test_file, parameter_index)

    path_cache_dir = test_dir / DEF_CACHE_DIR_NAME

    # PLANNED: serialize the func_args metadata recursively
    test_params = [*inspect.signature(request.node.function).parameters.keys()]
    func_args = {key: str(value) for key, value in request.node.funcargs.items() if key in test_params}
    metadata = {'test_file': test_file.as_posix(), 'test_name': test_name, 'func_args': func_args}

    # FYI: The keyword arguments can be overridden by the test function
    return partial(checks.assert_against_cache, path_cache_dir=path_cache_dir, cache_name=cache_name, metadata=metadata)
