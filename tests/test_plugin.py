"""Test plugin.py."""

import pytest


def test_check_assert_failure(fix_test_cache, with_check_assert):
    """Test that a difference in test_data and cached data generates an error."""
    kwargs = {
        'test_dir': fix_test_cache,
        'cache_name': 'test_check_assert_failure-00.json',
    }

    with_check_assert({'result': False}, **kwargs)  # act

    with pytest.raises(AssertionError):
        with_check_assert({'result': True}, **kwargs)
