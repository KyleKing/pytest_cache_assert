"""Test plugin.py."""

from pathlib import Path, PureWindowsPath

import pytest
from beartype import beartype


def test_assert_against_cache_failure(fix_test_cache, assert_against_cache):
    """Test that a difference in test_data and cached data generates an error."""
    kwargs = {
        'path_cache_dir': fix_test_cache / 'custom/nested/dir',
        'cache_name': 'test_assert_against_cache_failure-00.json',
    }

    assert_against_cache({'result': False}, **kwargs)  # act

    with pytest.raises(AssertionError):
        assert_against_cache({'result': True}, **kwargs)


@pytest.mark.parametrize(
    'test_data',
    [
        {'decorator': beartype},
        {'func': test_assert_against_cache_failure},
        {'path': Path.home()},
        {'PureWindowsPath': PureWindowsPath('C:/Program Files')},
    ],
)
def test_assert_against_cache(test_data, assert_against_cache):
    """Test edge cases for assert_against_cache."""
    assert_against_cache(test_data)
