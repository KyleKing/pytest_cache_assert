"""Test plugin.py."""

import pytest


def test_check_assert_failure(fix_test_cache, assert_against_cache):
    """Test that a difference in test_data and cached data generates an error."""
    kwargs = {
        'path_cache_dir': fix_test_cache / 'custom/nested/dir',
        'cache_name': 'test_check_assert_failure-00.json',
    }

    assert_against_cache({'result': False}, **kwargs)  # act

    with pytest.raises(AssertionError):
        assert_against_cache({'result': True}, **kwargs)
