"""Test plugin.py."""

import re
from datetime import datetime
from uuid import uuid4

import pendulum
import pytest
from beartype import beartype
from cerberus import Validator
from cerberus.schema import SchemaError

from pytest_cache_assert import KeyRule, check_suppress, check_type
from pytest_cache_assert._check_assert.constants import TEST_DATA_TYPE, Wildcards
from pytest_cache_assert._check_assert.differ import DiffResult
from pytest_cache_assert._check_assert.error_message import RichAssertionError
from pytest_cache_assert.main import assert_against_cache

# FIXME: Create a new plugin fixture that can store and access strings as keys in a dictionary
DEF_ERROR_MESSAGE = r'For test data: .*\nFound differences with: .*'


def test_assert_against_cache_failure(fix_tmp_assert):  # noqa: AAA01
    """Test that a difference in test_data and cached data generates an error."""
    cached_data = {'result': False}
    test_data = {'result': True}
    assert_against_cache(cached_data, **fix_tmp_assert)
    diff_results = [DiffResult(key_list=['result'], list_index=None, old=False, new=True)]
    error_info = None

    try:
        assert_against_cache(test_data, **fix_tmp_assert)
    except RichAssertionError as exc:
        error_info = exc.error_info

    assert error_info['test_data'] == test_data
    assert error_info['cached_data'] == cached_data
    assert error_info['path_cache_file'].name == fix_tmp_assert['cache_name']
    assert error_info['diff_results'] == diff_results


# -----------------------------------------------------------------------------
# Key Rules


@pytest.mark.parametrize(
    ('cached_data', 'test_data', 'key_rules'), [
        (
            {'title': 'hello'}, {'title': 'Hello World!'}, [
                KeyRule(pattern=['title'], func=check_suppress),
            ],
        ),  # Check suppressing a standard string
        (
            {'nested': {'title': 'hello'}}, {'nested': {'title': 'Hello World!'}}, [
                KeyRule(pattern=['nested', 'title'], func=check_suppress),
            ],
        ),  # Check suppressing nested changes
        (
            {'title': 'hello'}, {'added': {'nested': {'title': 'hello'}}}, [
                KeyRule(pattern=['added', Wildcards.SINGLE, Wildcards.SINGLE], func=check_suppress),
                KeyRule(pattern=['title'], func=check_suppress),
            ],
        ),  # Check wildcards
        (
            {}, {'added': {'recursive': {'title': 'hello'}}}, [
                KeyRule(pattern=['added', Wildcards.RECURSIVE], func=check_suppress),
            ],
        ),  # Check suppressing new value
        (
            {'number_list': [90, 91, 92, 96, 100]}, {'number_list': [90, 91, 92, 93, 94, 100]}, [
                KeyRule(pattern=['number_list'], func=check_suppress),
            ],
        ),
        (
            {'numbers': 20}, {'numbers': 45}, [
                KeyRule(pattern=['numbers'], func=check_type),
            ],
        ),  # Check matching number types
        (
            {'numbers': 20}, {'numbers': 45.0}, [
                KeyRule(pattern=['numbers'], func=check_type),
            ],
        ),  # Check different number types
        (
            {'numbers': '20'}, {'numbers': '45.0'}, [
                KeyRule(pattern=['numbers'], func=check_type),
            ],
        ),  # Check str(numbers) (Note: type checking does not differentiate between int and float)
        (
            {'uuid': str(uuid4())}, {'uuid': str(uuid4())}, [
                KeyRule(pattern=['uuid'], func=check_type),
            ],
        ),  # Check UUID types
        (
            {'dates': str(datetime.now())}, {'dates': str(pendulum.now().add(weeks=1))}, [
                KeyRule(pattern=['dates'], func=check_type),
            ],
        ),  # Check date types
        (
            {'dates': str(datetime.now())}, {'dates': None}, [
                KeyRule(pattern=['dates'], func=check_suppress),
            ],
        ),  # Suppress date/null
        (
            {'*': 50}, {'*': 51}, [
                KeyRule(pattern=['*'], func=check_type),
            ],
        ),  # Verify that asterisk keys work
    ],
)
def test_assert_against_cache_good_key_rules(cached_data, test_data, key_rules, fix_tmp_assert):
    """Test various edge cases for different dictionaries."""
    assert_against_cache(cached_data, **fix_tmp_assert)  # First Pass to Cache
    # Verify that the key_rules allow the test to pass
    assert_against_cache(test_data, key_rules=key_rules, **fix_tmp_assert)
    # Then, verify that without key rules, an AssertionError is raised

    with pytest.raises(AssertionError, match=DEF_ERROR_MESSAGE):
        assert_against_cache(test_data, **fix_tmp_assert)  # act


@pytest.mark.parametrize(
    ('cached_data', 'test_data', 'key_rules'), [
        (
            {'a': 50}, {'a': 51}, [
                KeyRule(pattern=['*'], func=check_type),
            ],
        ),  # Verify that asterisk keys work ('*' should not match 'a')
    ],
)
def test_assert_against_cache_bad_key_rules(cached_data, test_data, key_rules, fix_tmp_assert):
    """Test various edge cases for different dictionaries."""
    assert_against_cache(cached_data, **fix_tmp_assert)  # First Pass to Cache

    # Even with key_rules, the diff will fail
    with pytest.raises(AssertionError, match=DEF_ERROR_MESSAGE):
        assert_against_cache(test_data, key_rules=key_rules, **fix_tmp_assert)


def test_assert_against_cache_number_key_edge_case(fix_tmp_assert):
    """Dictionaries with keys that are numbers fail comparison because they are stringified on load."""
    cached_data = {10: 50}  # Will have key name 10 (number) removed, and '10' (string) added

    with pytest.raises(AssertionError, match=DEF_ERROR_MESSAGE):
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
