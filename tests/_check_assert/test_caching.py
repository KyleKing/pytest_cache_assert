"""Test caching.py."""

from pathlib import Path

import pytest

from pytest_cache_assert import main
from pytest_cache_assert._check_assert.caching import _merge_metadata, init_cache, load_cached_data, write_cache_data
from pytest_cache_assert._check_assert.constants import CACHE_README_TEXT, DEF_CACHE_DIR_NAME


def test_init_cache(fix_cache_path):
    """Test that the cache can be created."""
    init_cache(fix_cache_path / 'new_directory')  # act

    assert not (fix_cache_path / 'README.md').is_file()  # Only conditionally creates the README
    assert (fix_cache_path / 'new_directory' / 'README.md').read_text() == CACHE_README_TEXT


@pytest.mark.parametrize(
    'test_data',
    [
        {'number': 1.23, 'str': 'message', 'bool': True, 'null': None},
    ],
)
def test_caching(test_data, fix_cache_path):
    """Test that data can be cached and then restored."""
    init_cache(fix_cache_path)
    path_cache_file = fix_cache_path / 'a_dir/sample.json'
    write_cache_data(path_cache_file, metadata={}, test_data=test_data)

    result = load_cached_data(path_cache_file)

    assert result == test_data


@pytest.mark.parametrize(
    ('new_metadata', 'metadata_list'), [
        ({'new': 1}, [{'new': 1}, {'new': 2}]),  # Check Duplicate Removal
        ({'new': 2}, [{'new': 3}, {'zz': 0}, {'new': 2}, {'new': 1}]),  # Check Sorting
    ],
)
def test_merge_metadata(new_metadata, metadata_list):
    """Test _merge_metadata."""
    path_cache_dir = Path(__file__).parent / DEF_CACHE_DIR_NAME
    cache_name = f"test_merge_metadata-{new_metadata['new']}.json"

    result = _merge_metadata(new_metadata, metadata_list)

    # FYI: Can't use plugin here because of recursion by calling `_merge_metadata` twice
    main.assert_against_cache(result, path_cache_dir=path_cache_dir, cache_name=cache_name)


@pytest.mark.parametrize('index', range(3))
def test_repeated_caching(index, assert_against_cache):
    """Test that repeated caching to the same file works as expected."""
    assert_against_cache({'index': 2}, metadata={'index': index}, cache_name='caching/repeated_caching.json')  # act
