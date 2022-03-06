"""Test plugin.py."""

from pathlib import Path, PureWindowsPath

import pytest
from beartype import beartype
from pydantic import BaseModel

from pytest_cache_assert._check_assert.config import CacheAssertContainerKeys


def test_assert_against_cache_failure(fix_cache_path, assert_against_cache):
    """Test that a difference in test_data and cached data generates an error."""
    kwargs = {
        'path_cache_dir': fix_cache_path / 'custom/nested/dir',
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
        {'enum': CacheAssertContainerKeys.CONFIG},
        {'list_of_things': (Path.home(), 1.23, CacheAssertContainerKeys.CONFIG)},
        {'empty_list': []},
        {'empty_dict': {}},
        {'BaseModel': BaseModel},
        # Add test cases from Hypothesis
        {'1': False, '餁': 28498688},
        {'': False, '1': 0, '│\U00108f79': 0},
    ],
)
def test_assert_against_cache(test_data, assert_against_cache, benchmark):
    """Test edge cases for assert_against_cache."""
    benchmark(assert_against_cache, test_data)
