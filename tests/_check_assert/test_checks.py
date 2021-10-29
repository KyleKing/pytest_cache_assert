"""Test checks.py."""

from pathlib import Path

import pytest

from pytest_cache_assert._check_assert.checks import check_assert


def test_check_assert_failure(fix_test_cache):
    """Test that a difference in test_data and cached data generates an error."""
    # PLANNED: This logic should be implemented through introspection and not in the test code each time!!
    path_cache_dir = fix_test_cache / 'assert-cache'
    parameter_index = 0
    path_cache_file = path_cache_dir / f'{Path(__file__).stem}/test_check_assert_failure-{parameter_index:3}.json'
    kwargs = {
        'path_cache_dir': path_cache_dir,
        'path_cache_file': path_cache_file,
    }

    check_assert({'result': False}, **kwargs)  # act

    with pytest.raises(AssertionError):
        check_assert({'result': True}, **kwargs)
