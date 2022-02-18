"""PyTest configuration."""

from pathlib import Path

import pytest
from beartype.typing import Any, Callable, Dict
from calcipy.dev.conftest import pytest_configure  # noqa: F401
from calcipy.dev.conftest import pytest_html_results_table_header  # noqa: F401
from calcipy.dev.conftest import pytest_html_results_table_row  # noqa: F401
from calcipy.dev.conftest import pytest_runtest_makereport  # noqa: F401

from pytest_cache_assert import DEF_CACHE_DIR_KEY, DEF_CACHE_DIR_NAME

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

    Args:
        fix_test_cache: pytest fixture for temporary directory

    Returns:
        Path: Path to the test cache directory

    """
    return {
        'path_cache_dir': fix_test_cache,
        'cache_name': 'test_assert_against_cache.json',
    }


@pytest.fixture(scope='module')
def cache_assert_config() -> Dict[str, Any]:
    """Specify a custom cache directory."""
    return {  # noqa: DAR201
        DEF_CACHE_DIR_KEY: f'{DEF_CACHE_DIR_NAME}-custom',
    }
