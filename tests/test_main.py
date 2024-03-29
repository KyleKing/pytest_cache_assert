"""Test plugin.py."""

import re
from datetime import datetime
from uuid import uuid4

import arrow
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pytest_cache_assert import AssertRule, check_suppress, check_type
from pytest_cache_assert._check_assert.differ import DiffResults
from pytest_cache_assert._check_assert.error_message import RichAssertionError
from pytest_cache_assert.main import assert_against_cache, assert_against_dict

from .configuration import clear_test_cache

DEF_ERROR_MESSAGE = r'^\n> Found differences with: .+\n> Differences: .+'


def test_assert_against_cache_failure(fix_tmp_assert):  # noqa: AAA01
    """Test that a difference in test_data and cached data generates an error."""
    cached_data = {'result': False}
    test_data = {'result': True}
    assert_against_cache(cached_data, **fix_tmp_assert)
    diff_results = DiffResults(results={'values_changed': {"root['result']": {'new_value': True, 'old_value': False}}})
    error_info = None

    try:
        assert_against_cache(test_data, **fix_tmp_assert)
    except RichAssertionError as exc:
        error_info = exc.error_info

    assert error_info['test_data'] == test_data
    assert error_info['cached_data'] == cached_data
    assert error_info['path_cache_file'].name == fix_tmp_assert['cache_name']
    assert error_info['diff_results'] == diff_results


def test_assert_against_dict():
    """Quick check that the in-memory assert works as expected."""
    old = {'key': 1, 'keys': [{'nested': 2}]}
    new = {'key': 1, 'keys': [{'nested': 2}]}

    assert_against_dict(old, new)


# -----------------------------------------------------------------------------
# Key Rules


@pytest.mark.parametrize(
    ('cached_data', 'test_data', 'assert_rules', 'help_text'), [
        (
            {'title': 'hello'}, {'title': 'Hello World!'}, [
                AssertRule(pattern="root['title']", func=check_suppress),
            ], 'Check suppressing a standard string',
        ),
        (
            {'nested': {'title': 'hello'}}, {'nested': {'title': 'Hello World!'}}, [
                AssertRule(pattern="root['nested']['title']", func=check_suppress),
            ], 'Check suppressing nested changes',
        ),
        (
            {'top': {'nested': {'inner': []}}}, {'top': {'nested': {'title': 'hello'}}}, [
                AssertRule(pattern=re.compile(r"root\['top'\](?:\[[^\]]+\]){2}"), func=check_suppress),
            ], 'Check missing and added',
        ),
        (
            {'title': 'hello'}, {'added': {'nested': {'title': 'hello'}}}, [
                AssertRule(pattern='added', func=check_suppress),
                AssertRule(pattern='title', func=check_suppress),
            ], 'Check missing and added',
        ),
        (
            {}, {'added': {'recursive': {'title': 'hello'}}}, [
                AssertRule(pattern=re.compile(r'added.+'), func=check_suppress),
            ], 'Check suppressing new value',
        ),
        (
            {'number_list': [90, 91, 92, 96, 100]}, {'number_list': [90, 91, 92, 93, 94, 100]}, [
                AssertRule(pattern="root['number_list']", func=check_suppress),
            ], 'Check matching number types (1)',
        ),
        (
            {'numbers': 20}, {'numbers': 45}, [
                AssertRule(pattern='numbers', func=check_type),
            ], 'Check matching number types (2)',
        ),
        (
            {'numbers': 20}, {'numbers': 45.0}, [
                AssertRule(pattern='numbers', func=check_type),
            ], 'Check different number types',
        ),
        (
            {'numbers': '20'}, {'numbers': '45.0'}, [
                AssertRule(pattern='numbers', func=check_type),
            ], 'Check str(numbers) (Note: type checking does not differentiate between int and float)',
        ),
        (
            {'uuid': str(uuid4())}, {'uuid': str(uuid4())}, [
                AssertRule(pattern='uuid', func=check_type),
            ], 'Check UUID types',
        ),
        (
            {'dates': str(datetime.now())}, {'dates': str(arrow.now().shift(weeks=1))}, [  # noqa: DTZ005
                AssertRule(pattern='dates', func=check_type),
            ], 'Check date types',
        ),
        (
            {'dates': str(datetime.now())}, {'dates': None}, [  # noqa: DTZ005
                AssertRule(pattern='dates', func=check_suppress),
            ], 'Suppress date/null',
        ),
        (
            {'*': 50}, {'*': 51}, [
                AssertRule(pattern=re.compile('.+'), func=check_type),
            ], 'Verify that asterisk keys work',
        ),
    ],
)
def test_assert_against_cache_good_key_rules(cached_data, test_data, assert_rules, help_text, fix_tmp_assert):
    """Test various edge cases for different dictionaries."""
    assert_against_cache(cached_data, **fix_tmp_assert)  # First Pass to Cache
    # Verify that the assert_rules allow the test to pass
    try:
        assert_against_cache(test_data, assert_rules=assert_rules, **fix_tmp_assert)
    except Exception as exc:
        raise AssertionError(f'Failed {help_text}') from exc

    # Then, verify that without assert rules, an AssertionError is raised
    with pytest.raises(AssertionError, match=DEF_ERROR_MESSAGE):  # noqa: PT012
        assert_against_cache(test_data, **fix_tmp_assert)  # act
        msg = f'Failed to raise an AssertionError for: {help_text}'
        raise RuntimeError(msg)


@pytest.mark.parametrize(
    ('cached_data', 'test_data', 'assert_rules'), [
        (
            {'a': 50}, {'a': 51}, [
                AssertRule(pattern='.', func=check_type),
            ],
        ),
    ],
    ids=[
        'Verify that regex is only used for compiled patterns (i.e. "." should not match "a")',
    ],
)
def test_assert_against_cache_bad_key_rules(cached_data, test_data, assert_rules, fix_tmp_assert):
    """Test various edge cases for different dictionaries."""
    assert_against_cache(cached_data, **fix_tmp_assert)  # First Pass to Cache

    # Even with assert_rules, the diff will fail
    with pytest.raises(AssertionError, match=DEF_ERROR_MESSAGE):
        assert_against_cache(test_data, assert_rules=assert_rules, **fix_tmp_assert)


# -----------------------------------------------------------------------------
# Hypothesis Testing


# TODO: Add tests for additional types: st.binary(), etc.
#   https://hypothesis.readthedocs.io/en/latest/ghostwriter.html
#   https://hypothesis.readthedocs.io/en/latest/data.html
@settings(
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    result=st.dictionaries(
        keys=st.text(),
        values=(st.booleans() | st.integers() | st.text() | st.binary()),
        max_size=5,
    ),
)
def test_assert_against_cache_with_hypothesis(result, fix_tmp_assert):
    """Test edge cases for assert_against_cache with hypothesis."""
    clear_test_cache()  # Function scope fixtures are not reset, so manually clear
    assert_against_cache(result, **fix_tmp_assert)

    try:
        assert_against_cache(result, **fix_tmp_assert)  # act
    except Exception as exc:
        cached_text = (fix_tmp_assert['path_cache_dir'] / fix_tmp_assert['cache_name']).read_text()
        raise AssertionError(f'Failed to find assertion match for `{result}` against:\n\n{cached_text}') from exc
