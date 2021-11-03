"""Test the differ logic."""

from datetime import datetime, timedelta

import pytest

from pytest_cache_assert import KeyRule, Wildcards, check_suppress
from pytest_cache_assert._check_assert.constants import TrueNull
from pytest_cache_assert._check_assert.differ import DiffResult, _raw_diff, diff_with_rules
from pytest_cache_assert._check_assert.key_rules import Comparator, gen_check_date_proximity, gen_check_date_range


@pytest.mark.parametrize(
    ('old_dict', 'new_dict', 'expected'), [
        (
            {'title': 'hello'}, {'title': 'Hello World!'}, [
                DiffResult(key_list=['title'], list_index=None, old='hello', new='Hello World!'),
            ],
        ),  # Minor string difference
        (
            {'nest1': {'nest2': {'title': 'hello'}}}, {'nest1': {'nest2': {'title': 'Hello World!'}}}, [
                DiffResult(key_list=['nest1', 'nest2', 'title'], list_index=None, old='hello', new='Hello World!'),
            ],
        ),  # Minor string difference with nesting
        (
            {'numbers': '20'}, {'numbers': 20}, [
                DiffResult(key_list=['numbers'], list_index=None, old='20', new=20),
            ],
        ),  # String vs. int
        (
            {'numbers': 20}, {'numbers': 45}, [
                DiffResult(key_list=['numbers'], list_index=None, old=20, new=45),
            ],
        ),  # Difference in numbers
        ({'numbers': 20.0}, {'numbers': 20}, []),  # No Diff on numeric float vs int
        (
            {'10': 50}, {'10': 51}, [
                DiffResult(key_list=['10'], list_index=None, old=50, new=51),
            ],
        ),  # Test with string numbers keys
        (
            {'number_list': [90, 91, 92, 96, 100]}, {'number_list': [90, 91, 92, 93, 94, 100]}, [
                DiffResult(key_list=['number_list'], list_index=3, old=96, new=93),
                DiffResult(key_list=['number_list'], list_index=4, old=100, new=94),
                DiffResult(key_list=['number_list'], list_index=5, old=TrueNull, new=100),
            ],
        ),  # Test with specific list indices
        (
            {'fruits': []}, {'fruits': ['apple', 'mango']}, [
                DiffResult(key_list=['fruits'], list_index=0, old=TrueNull, new='apple'),
                DiffResult(key_list=['fruits'], list_index=1, old=TrueNull, new='mango'),
            ],
        ),  # Sample from the dictdiffer docs
        (
            {'missing': {'title': 'hello'}}, {'title': 'hello'}, [
                DiffResult(key_list=['title'], list_index=None, old=TrueNull, new='hello'),
                DiffResult(key_list=['missing', 'title'], list_index=None, old='hello', new=TrueNull),
            ],
        ),  # Test with missing data and added data (1)
        (
            {'title': 'hello'}, {'added': {'nested': {'title': 'hello'}}}, [
                DiffResult(key_list=['title'], list_index=None, old='hello', new=TrueNull),
                DiffResult(key_list=['added', 'nested', 'title'], list_index=None, old=TrueNull, new='hello'),
            ],
        ),  # Test with missing data and added data (2)
        (
            {'list': ['acorn', 'tree']}, {'list': ['acorn', 'treenut']}, [
                DiffResult(key_list=['list'], list_index=1, old='tree', new='treenut'),
            ],
        ),  # Test difference in value in list
        (
            {'iterable': {'tree', 'acorn'}}, {'iterable': ['tree', 'acorn']}, [
                DiffResult(key_list=['iterable'], list_index=None, old={'tree', 'acorn'}, new=['tree', 'acorn']),
            ],
        ),  # Test with a set vs. a list (though this won't work with JSON)
        (
            {'nullable': None}, {'nullable': 'Not Null'}, [
                DiffResult(key_list=['nullable'], list_index=None, old=None, new='Not Null'),
            ],
        ),  # Test with Null
        (
            {'a': [{'list': 1}, {'list': None}]}, {'a': [{'list': 1}, {'list': 2}]}, [
                DiffResult(key_list=['a', 1, 'list'], list_index=None, old=None, new=2),
            ],
        ),  # Test with dictionaries in lists
        (
            {'a': [{'b': [{'c': 1}]}]}, {'a': [{'b': [{'c': 2}]}]}, [
                DiffResult(key_list=['a', 0, 'b', 0, 'c'], list_index=None, old=1, new=2),
            ],
        ),  # Test with nested lists of dicts of lists
        (
            {'a': [{'list': 1}, {'list': 2}]}, {'a': [{'list': 3}, {'list': 4}]}, [
                DiffResult(key_list=['a', 0, 'list'], list_index=None, old=1, new=3),
                DiffResult(key_list=['a', 1, 'list'], list_index=None, old=2, new=4),
            ],
        ),  # Test multiple differences in dictionaries in lists
    ],
)
def test_raw_diff(old_dict, new_dict, expected):
    """Test the low level diff logic."""
    result = _raw_diff(old_dict=old_dict, new_dict=new_dict)

    assert sorted(result) == sorted(expected)


_NOW = datetime.utcnow()


@pytest.mark.parametrize(
    ('old_dict', 'new_dict', 'key_rules'), [
        (
            {'a': {'b': {'c': None}}}, {'a': {'b': {'c': 'Not Null'}}}, [
                KeyRule(pattern=['a', Wildcards.RECURSIVE]),
                KeyRule(pattern=['a', 'b', 'c'], func=check_suppress),
                KeyRule(pattern=['a', Wildcards.SINGLE, Wildcards.SINGLE]),
            ],
        ),  # Check Sorting. Only the middle key_rule will suppress the error
        (
            {'a': [{'b': [{'c': 1}]}]}, {'a': [{'b': [{'c': 2}]}]}, [
                KeyRule(
                    pattern=['a', Wildcards.LIST, 'b', Wildcards.LIST, 'c'],
                    func=check_suppress,
                ),
            ],
        ),  # Supports Wildcards.LIST
        (
            {'a': [{'b': [{'c': 1}]}]}, {'a': [{'b': [{'c': 2}]}]}, [
                KeyRule(
                    pattern=['a', Wildcards.LIST, Wildcards.RECURSIVE],
                    func=check_suppress,
                ),
            ],
        ),  # Supports Wildcards.LIST
        (
            {'a.b.c': 1}, {'a.b.c': 2}, [
                KeyRule(pattern=['a.b.c'], func=check_suppress),
            ],
        ),  # Supports dotted-key names
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW + timedelta(hours=3))}, [
                KeyRule(pattern=['datetime'], func=gen_check_date_range(max_date=_NOW + timedelta(hours=3))),
            ],
        ),  # Test generated datetime comparison logic for a max date
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW - timedelta(hours=3))}, [
                KeyRule(
                    pattern=['datetime'],
                    func=gen_check_date_range(_NOW + timedelta(hours=3), _NOW + timedelta(hours=3)),
                ),
            ],
        ),  # Test generated datetime comparison logic for a date range
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW + timedelta(hours=3))}, [
                KeyRule(pattern=['datetime'], func=gen_check_date_proximity(timedelta(hours=3), Comparator.LTE)),
            ],
        ),  # Test generated datetime comparison logic for LTE
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW - timedelta(hours=3))}, [
                KeyRule(pattern=['datetime'], func=gen_check_date_proximity(timedelta(hours=3), Comparator.LTE)),
            ],
        ),  # Test generated datetime comparison logic for GTE
        (
            {'datetime': str(_NOW)}, {'datetime': str(_NOW + timedelta(hours=3))}, [
                KeyRule(pattern=['datetime'], func=gen_check_date_proximity(timedelta(hours=3))),
            ],
        ),  # Test generated datetime comparison logic for Within
    ],
)
def test_diff_with_rules(old_dict, new_dict, key_rules):
    """Test that the key rules work in various scenarios."""
    result = diff_with_rules(old_dict=old_dict, new_dict=new_dict, key_rules=key_rules)

    assert result == []
    errors = diff_with_rules(old_dict=old_dict, new_dict=new_dict, key_rules=[])
    assert len(errors) == 1
