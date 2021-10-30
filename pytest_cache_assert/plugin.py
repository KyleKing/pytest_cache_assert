"""Pytest Plugin."""

from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict

import pytest
from _pytest.fixtures import FixtureRequest
from beartype import beartype

from ._check_assert.caching import resolve_cache_name
from .checks import check_assert

# PLANNED: Provide CLI args return request.config.getoption("--record-mode") or "none"
# https://github.com/kiwicom/pytest-recording/blob/484bb887dd43fcaf44149160d57b58a7215e2c8a/src/pytest_recording/plugin.py#L37-L70


@pytest.fixture(scope='session')
def check_assert_parameter_counter() -> Dict[str, int]:
    """Track the times each specific test function has been run."""
    # PLANNED: Should be a class, but a dictionary is fine for now
    counter: Dict[str, int] = {}
    return counter


@pytest.fixture()
@beartype
def with_check_assert(
    request: FixtureRequest,
    check_assert_parameter_counter: Dict[str, int],
) -> Callable[[Any], None]:
    """Yield check_assert with pytest-specific arguments already specified.

    Args:
        request: pytest fixture used to identify the test directory
        check_assert_parameter_counter: pytest fixture used to track the current parameter index

    Returns:
        Callable[[Any], None]: `check_assert()` with test_dir already specified

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

    # PLANNED: serialize the metadata recursively
    func_args = {key: str(value) for key, value in request.node.funcargs.items()}
    metadata = {'test_file': test_file.as_posix(), 'test_name': test_name, 'func_args': func_args}

    # FYI: The keyword arguments can be overridden by the test function
    return partial(check_assert, test_dir=test_dir, cache_name=cache_name, metadata=metadata)
