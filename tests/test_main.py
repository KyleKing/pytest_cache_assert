"""Test plugin.py."""

import re
from datetime import datetime
from uuid import uuid4

import pytest
from beartype import beartype
from cerberus import Validator
from cerberus.schema import SchemaError

from pytest_cache_assert import KeyRule, check_suppress, check_type
from pytest_cache_assert._check_assert.constants import TEST_DATA_TYPE
from pytest_cache_assert.main import assert_against_cache

# TODO: Make a smarter error message parser for better verification or result
DEF_ERROR_MESSAGE = r'For test data: .*\nFound differences with: .*'


def test_assert_against_cache_failure(fix_tmp_assert):
    """Test that a difference in test_data and cached data generates an error."""
    assert_against_cache({'result': False}, **fix_tmp_assert)

    with pytest.raises(AssertionError, match=DEF_ERROR_MESSAGE):
        assert_against_cache({'result': True}, **fix_tmp_assert)  # act


# -----------------------------------------------------------------------------
# Key Rules


@pytest.mark.parametrize(
    ('cached_data', 'test_data', 'key_rules'), [
        (
            {'title': 'hello'}, {'title': 'Hello World!'}, [
                KeyRule(key_list=['title'], func=check_suppress),
            ],
        ),
        (
            {'nested': {'title': 'hello'}}, {'nested': {'title': 'Hello World!'}}, [
                KeyRule(key_list=['nested', 'title'], func=check_suppress),
            ],
        ),
        (
            {'title': 'hello'}, {'added': {'nested': {'title': 'hello'}}}, [
                KeyRule(key_list=['added', '*', '*'], func=check_suppress),
                KeyRule(key_list=['title'], func=check_suppress),
            ],
        ),
        (
            {'numbers': 20}, {'numbers': 45}, [
                KeyRule(key_list=['numbers'], func=check_type),
            ],
        ),
        (
            {'uuid': str(uuid4())}, {'uuid': str(uuid4())}, [
                KeyRule(key_list=['uuid'], func=check_type),
            ],
        ),
        (
            {'numbers': '20.0'}, {'numbers': '45.0'}, [
                KeyRule(key_list=['numbers'], func=check_type),  # PLANNED: Demonstrate that int != float?
            ],
        ),
        # ({'number_list': [90, 91, 92, 96, 100]}, {'number_list': [90, 91, 92, 93, 94, 100]}, [
        #     KeyRule(key_list=['dates'], func=check_type),  # FIXME: Need logic for lists!
        # ]),
        (
            {'dates': str(datetime.now())}, {'dates': str(datetime.utcnow())}, [
                KeyRule(key_list=['dates'], func=check_type),
            ],
        ),
        # ({'list': ['acorn', 'tree']}, {'list': ['acorn', 'treenut']}, []),
        # ({'dates': None}, {'dates': str(datetime.utcnow())}, []),
        # ({'dates': str(datetime.utcnow())}, {'dates': None}, []),
        # ({'10': 50}, {'10': 51}, []),
    ],
)
def test_assert_against_cache_differ(cached_data, test_data, key_rules, fix_tmp_assert):
    """Test various edge cases for different dictionaries."""
    assert_against_cache(cached_data, **fix_tmp_assert)  # First Pass to Cache
    # Verify that the key_rules allow the test to pass
    assert_against_cache(test_data, key_rules=key_rules, **fix_tmp_assert)

    # Verify that without key rules, an AssertionError is raised
    with pytest.raises(AssertionError, match=DEF_ERROR_MESSAGE):
        assert_against_cache(test_data, **fix_tmp_assert)  # act


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
