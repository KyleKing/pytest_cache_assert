"""Test plugin.py."""

import re
from datetime import datetime

import pendulum
import pytest
from beartype import beartype
from cerberus import Validator
from cerberus.schema import SchemaError

from pytest_cache_assert._check_assert.constants import TEST_DATA_TYPE
from pytest_cache_assert.main import assert_against_cache


def test_assert_against_cache_failure(fix_tmp_assert):
    """Test that a difference in test_data and cached data generates an error."""
    assert_against_cache({'result': False}, **fix_tmp_assert)

    with pytest.raises(AssertionError, match=r'For test data: .*\nFound differences with: .*'):
        assert_against_cache({'result': True}, **fix_tmp_assert)  # act


# -----------------------------------------------------------------------------
# Key Rules

# assert list(result) == [
#     ('change', ['settings', 'assignees', 2], (201, 202)),
#     ('add', 'stargazers', [(2, '/users/40')]),
#     ('change', 'title', ('hello', 'hellooo'))]

# TODO: Parametrize this test!
@pytest.mark.parametrize(('cached_data', 'test_data', 'key_rules'), [
    # TODO: Key Rule
    ({'title': 'hello'}, {'title': 'Hello World!'}, {}),
    ({'nested': {'title': 'hello'}}, {'nested': {'title': 'Hello World!'}}, {}),
    ({'missing': {'title': 'hello'}}, {'title': 'hello'}, {}),
    ({'title': 'hello'}, {'added': {'title': 'hello'}}, {}),
    ({'numbers': 20}, {'numbers': 45}, {}),
    ({'number_list': [90, 91, 92, 96, 100]}, {'number_list': [90, 91, 92, 93, 94, 100]}, {}),
    ({'list': ['acorn', 'tree']}, {'list': ['acorn', 'treenut']}, {}),
    ({'iterable': {'acorn', 'tree'}}, {'iterable': ['acorn', 'tree']}, {}),
    ({'dates': str(pendulum.now())}, {'dates': str(pendulum.now())}, {}),
    ({'dates': str(datetime.utcnow())}, {'dates': str(datetime.utcnow())}, {}),
    ({'dates': None}, {'dates': str(datetime.utcnow())}, {}),
    ({'dates': str(datetime.utcnow())}, {'dates': None}, {}),
    ({'10': 50}, {'10': 51}, {}),
])
def test_assert_against_cache_differ(cached_data, test_data, key_rules, fix_tmp_assert):
    """Test various edge cases for different dictionaries."""
    fix_tmp_assert = {**fix_tmp_assert, 'key_rules': key_rules}
    assert_against_cache(cached_data, **fix_tmp_assert)  # Cache

    with pytest.raises(AssertionError, match=r'For test data: .*\nFound differences with: .*'):
        assert_against_cache(test_data, **fix_tmp_assert)  # act


def test_assert_against_cache_number_key_edge_case(fix_tmp_assert):
    """Dictionaries with keys that are numbers fail comparison because they are stringified on load."""
    cached_data = {10: 50}  # Will have key name 10 (number) removed, and '10' (string) added

    with pytest.raises(AssertionError, match=r'For test data: .*\nFound differences with: .*'):
        assert_against_cache(cached_data, **fix_tmp_assert)  # act


# -----------------------------------------------------------------------------
# Validators


@beartype
def cerberus_validator(test_data: TEST_DATA_TYPE) -> None:
    """Cerberus custom validator example."""
    validator = Validator({'result': {'type': 'int'}})
    assert validator.validate(test_data)


def test_assert_against_cache_validator(fix_tmp_assert):
    """Test the validator."""
    expected = re.escape("{'result': [{'type': ['Unsupported types: int']}]}")

    with pytest.raises(SchemaError, match=expected):
        assert_against_cache({'result': False}, validator=cerberus_validator, **fix_tmp_assert)  # act
