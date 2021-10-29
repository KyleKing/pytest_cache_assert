"""Test caching.py."""

import pytest

from pytest_cache_assert._check_assert.caching import cache_data, init_cache, load_cached_data
from pytest_cache_assert._check_assert.constants import CACHE_README_TEXT


def test_init_cache(fix_test_cache):
    """Test that the cache can be created."""
    init_cache(fix_test_cache)  # act

    assert (fix_test_cache / 'README.md').read_text() == CACHE_README_TEXT


@pytest.mark.parametrize(
    'test_data',
    [
        {'number': 1.23, 'str': 'message', 'bool': True, 'null': None},
    ],
)
def test_caching(test_data, fix_test_cache):
    """Test that data can be cached and then restored."""
    init_cache(fix_test_cache)
    path_cache_file = fix_test_cache / 'a_dir/sample.json'
    cache_data(path_cache_file, {}, test_data)

    result = load_cached_data(path_cache_file)

    assert result == test_data
