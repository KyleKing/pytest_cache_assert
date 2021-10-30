"""Pytest Plugin."""

from functools import partial
from typing import Any, Callable

import pytest
from _pytest.fixtures import FixtureRequest
from beartype import beartype

from .checks import check_assert

# PLANNED: Provide CLI args return request.config.getoption("--record-mode") or "none"
# https://github.com/kiwicom/pytest-recording/blob/484bb887dd43fcaf44149160d57b58a7215e2c8a/src/pytest_recording/plugin.py#L37-L70


@pytest.fixture()
@beartype
def with_check_assert(request: FixtureRequest) -> Callable[[Any], None]:
    """Yield check_assert with pytest-specific arguments already specified.

    Args:
        request: pytest fixture used to identify the test directory

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

    return partial(check_assert, test_dir=test_dir)
