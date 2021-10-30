"""Test plugin.py."""

import pytest

from pytest_cache_assert.checks import assert_against_cache


def test_assert_against_cache(fix_test_cache):
    """Test that a difference in test_data and cached data generates an error."""
    kwargs = {
        'path_cache_dir': fix_test_cache,
        'cache_name': 'test_assert_against_cache.json',
    }

    assert_against_cache({'result': False}, **kwargs)  # act

    with pytest.raises(AssertionError):
        assert_against_cache({'result': True}, **kwargs)
