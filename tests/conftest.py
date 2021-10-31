"""PyTest configuration."""

from pathlib import Path
from typing import Callable

import pytest
from calcipy.dev.conftest import pytest_configure  # noqa: F401
from calcipy.dev.conftest import pytest_html_results_table_header  # noqa: F401
from calcipy.dev.conftest import pytest_html_results_table_row  # noqa: F401
from calcipy.dev.conftest import pytest_runtest_makereport  # noqa: F401

from .configuration import TEST_TMP_CACHE, clear_test_cache


@pytest.fixture()
def fix_test_cache() -> Path:
    """Fixture to clear and return the test cache directory for use.

    Returns:
        Path: Path to the test cache directory

    """
    clear_test_cache()
    return TEST_TMP_CACHE


@pytest.fixture()
def fix_tmp_assert(fix_test_cache: Callable[[None], Path]) -> Path:
    """Fixture to temporary assert directory and keyword arguments.

    Returns:
        Path: Path to the test cache directory

    """
    return {
        'path_cache_dir': fix_test_cache,
        'cache_name': 'test_assert_against_cache.json',
    }
