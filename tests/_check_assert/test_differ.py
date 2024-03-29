"""Test the differ logic."""

import re
from datetime import datetime, timedelta

import pytest

from pytest_cache_assert import AssertRule, check_exact, check_suppress
from pytest_cache_assert._check_assert.assert_rules import Comparator, gen_check_date_proximity, gen_check_date_range
from pytest_cache_assert._check_assert.differ import DiffResults, _raw_diff, diff_with_rules


@pytest.mark.parametrize(
    ('old_dict', 'new_dict', 'expected', 'help_text'), [
        (
            {'title': 'hello'}, {'title': 'Hello World!'},
            DiffResults(
                results={
                    'values_changed': {
                        "root['title']": {
                            'new_value': 'Hello World!',
                            'old_value': 'hello',
                        },
                    },
                },
            ),
            'Minor string difference',
        ),
        (
            {'nest1': {'nest2': {'title': 'hello'}}}, {'nest1': {'nest2': {'title': 'Hello World!'}}},
            DiffResults(
                results={
                    'values_changed': {
                        "root['nest1']['nest2']['title']": {
                            'new_value': 'Hello World!',
                            'old_value': 'hello',
                        },
                    },
                },
            ),
            'Minor string difference with nesting',
        ),
        (
            {'numbers': '20'}, {'numbers': 20},
            DiffResults(
                results={
                    'type_changes': {
                        "root['numbers']": {
                            'old_type': str,
                            'new_type': int,
                            'old_value': '20',
                            'new_value': 20,
                        },
                    },
                },
            ),
            'String vs. int',
        ),
        (
            {'numbers': 20}, {'numbers': 45},
            DiffResults(results={'values_changed': {"root['numbers']": {'new_value': 45, 'old_value': 20}}}),
            'Difference in numbers',
        ),
        (
            {'numbers': 20.0}, {'numbers': 20},
            DiffResults(
                results={
                    'type_changes': {
                        "root['numbers']": {
                            'old_type': float,
                            'new_type': int,
                            'old_value': 20.0,
                            'new_value': 20,
                        },
                    },
                },
            ),
            'Diff on numeric float vs int',
        ),
        (
            {'10': 50}, {'10': 51},
            DiffResults(results={'values_changed': {"root['10']": {'new_value': 51, 'old_value': 50}}}),
            'Test with string numbers keys',
        ),
        (
            {'number_list': [90, 91, 92, 96, 100]}, {'number_list': [90, 91, 92, 93, 94, 100]},
            DiffResults(
                results={
                    'values_changed': {
                        "root['number_list'][3]": {
                            'new_value': 93, 'old_value': 96,
                        },
                    }, 'iterable_item_added': {
                        "root['number_list'][4]": 94,
                    },
                },
            ),
            'Test with specific list indices',
        ),
        (
            {'fruits': []}, {'fruits': ['apple', 'mango']},
            DiffResults(results={'iterable_item_added': {"root['fruits'][0]": 'apple', "root['fruits'][1]": 'mango'}}),
            'Sample from the dictdiffer docs',
        ),
        (
            {'missing': {'title': 'hello'}}, {'title': 'hello'},
            DiffResults(
                results={
                    'dictionary_item_added': ["root['title']"],
                    'dictionary_item_removed': ["root['missing']"],
                },
            ),
            'Test with missing data and added data (1)',
        ),
        (
            {'title': 'hello'}, {'added': {'nested': {'title': 'hello'}}},
            DiffResults(
                results={
                    'dictionary_item_added': ["root['added']"],
                    'dictionary_item_removed': ["root['title']"],
                },
            ),
            'Test with missing data and added data (2)',
        ),
        (
            {'list': ['acorn', 'tree']}, {'list': ['acorn', 'treenut']},
            DiffResults(results={'values_changed': {"root['list'][1]": {'new_value': 'treenut', 'old_value': 'tree'}}}),
            'Test difference in value in list',
        ),
        (
            {'iterable': {'tree', 'acorn'}}, {'iterable': ['tree', 'acorn']},
            DiffResults(
                results={
                    'type_changes': {
                        "root['iterable']": {
                            'old_type': set,
                            'new_type': list,
                            'old_value': {
                                'tree',
                                'acorn',
                            },
                            'new_value': [
                                'tree',
                                'acorn',
                            ],
                        },
                    },
                },
            ),
            "Test with a set vs. a list (though this won't work with JSON)",
        ),
        (
            {'nullable': None}, {'nullable': 'Not Null'},
            DiffResults(
                results={
                    'type_changes': {
                        "root['nullable']": {
                            'old_type': type(None),
                            'new_type': str,
                            'old_value': None,
                            'new_value': 'Not Null',
                        },
                    },
                },
            ),
            'Test with Null',
        ),
        (
            {'a': [{'list': 1}, {'list': None}]}, {'a': [{'list': 1}, {'list': 2}]},
            DiffResults(
                results={
                    'type_changes': {
                        "root['a'][1]['list']": {
                            'old_type': type(None),
                            'new_type': int,
                            'old_value': None,
                            'new_value': 2,
                        },
                    },
                },
            ),
            'Test with dictionaries in lists',
        ),
        (
            {'a': [{'b': [{'c': 1}]}]}, {'a': [{'b': [{'c': 2}]}]},
            DiffResults(results={'values_changed': {"root['a'][0]['b'][0]['c']": {'new_value': 2, 'old_value': 1}}}),
            'Test with nested lists of dicts of lists',
        ),
        (
            {'a': [{'list': 1}, {'list': 2}]}, {'a': [{'list': 3}, {'list': 4}]},
            DiffResults(
                results={
                    'values_changed': {
                        "root['a'][0]['list']": {
                            'new_value': 3,
                            'old_value': 1,
                        },
                        "root['a'][1]['list']": {
                            'new_value': 4,
                            'old_value': 2,
                        },
                    },
                },
            ),
            'Test multiple differences in dictionaries in lists',
        ),
    ],
)
def test_raw_diff(old_dict, new_dict, expected, help_text):
    """Test the low level diff logic."""
    result = _raw_diff(old_dict=old_dict, new_dict=new_dict)

    try:
        assert result == expected
    except Exception as exc:
        raise AssertionError(f'Failed {help_text}') from exc


_NOW = datetime.utcnow()  # noqa: DTZ003


@pytest.mark.parametrize(
    ('old_dict', 'new_dict', 'assert_rules', 'help_text'), [
        (
            {'a': {'b': {'c': None}}}, {'a': {'b': {'c': 'Not Null'}}}, [
                AssertRule(pattern=re.compile(r"root\['a'\](?:\[[^]]\])+"), func=check_exact),
                AssertRule(pattern="root['a']['b']['c']", func=check_suppress),
                AssertRule(pattern=re.compile(r"root\['a'\](?:\[[^]]\]){2}"), func=check_exact),
            ], 'Check Sorting. Only the middle assert_rule will suppress the error',
        ),
        (
            {'a': [{'b': [{'c': 1}]}]}, {'a': [{'b': [{'c': 2}]}]}, [
                AssertRule(
                    pattern=re.compile(r"root\['a'\]\[\d+\]\['b'\]\[\d+\]\['c'\]"),
                    func=check_suppress,
                ),
            ], 'Supports Wildcards.LIST',
        ),
        (
            {'a': [{'b': [{'c': 1}]}]}, {'a': [{'b': [{'c': 2}]}]}, [
                AssertRule(
                    pattern=re.compile(r"root\['a'\]\[\d+\]\[.+"),
                    func=check_suppress,
                ),
            ], 'Supports Wildcards.LIST',
        ),
        (
            {'a.b.c': 1}, {'a.b.c': 2}, [
                AssertRule(pattern='a.b.c', func=check_suppress),
            ], 'Supports dotted-key names',
        ),
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW + timedelta(hours=3))}, [
                AssertRule(pattern='datetime', func=gen_check_date_range(max_date=_NOW + timedelta(hours=3))),
            ], 'Test generated datetime comparison logic for a max date',
        ),
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW - timedelta(hours=3))}, [
                AssertRule(
                    pattern='datetime',
                    func=gen_check_date_range(_NOW - timedelta(hours=3), _NOW + timedelta(hours=3)),
                ),
            ], 'Test generated datetime comparison logic for a date range',
        ),
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW + timedelta(hours=3))}, [
                AssertRule(pattern='datetime', func=gen_check_date_proximity(timedelta(hours=3), Comparator.LTE)),
            ], 'Test generated datetime comparison logic for LTE',
        ),
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW - timedelta(hours=3))}, [
                AssertRule(pattern='datetime', func=gen_check_date_proximity(timedelta(hours=3), Comparator.LTE)),
            ], 'Test generated datetime comparison logic for GTE',
        ),
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW + timedelta(hours=3))}, [
                AssertRule(pattern='datetime', func=gen_check_date_proximity(timedelta(hours=3))),
            ], 'Test generated datetime comparison logic for Within',
        ),
    ],
)
def test_diff_with_rules(old_dict, new_dict, assert_rules, help_text):
    """Test that the assert rules work in various scenarios."""
    result = diff_with_rules(old_dict=old_dict, new_dict=new_dict, assert_rules=assert_rules)
    assert result.to_dict() == {}

    try:
        errors = diff_with_rules(old_dict=old_dict, new_dict=new_dict, assert_rules=[])
    except Exception as exc:
        raise AssertionError(f'Failed {help_text}') from exc
    assert errors.to_dict() != {}
