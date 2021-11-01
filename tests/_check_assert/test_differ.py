"""Test the differ logic."""

import pytest

from pytest_cache_assert import KeyRule, Wildcards, check_suppress
from pytest_cache_assert._check_assert.constants import TrueNull
from pytest_cache_assert._check_assert.differ import DiffResult, _raw_diff, diff_with_rules


@pytest.mark.parametrize(
    ('old_dict', 'new_dict', 'expected'), [
        (
            {'title': 'hello'}, {'title': 'Hello World!'}, [
                DiffResult(key_list=['title'], list_index=None, old='hello', new='Hello World!'),
            ],
        ),
        (
            {'nest1': {'nest2': {'title': 'hello'}}}, {'nest1': {'nest2': {'title': 'Hello World!'}}}, [
                DiffResult(key_list=['nest1', 'nest2', 'title'], list_index=None, old='hello', new='Hello World!'),
            ],
        ),
        (
            {'numbers': 20}, {'numbers': 45}, [
                DiffResult(key_list=['numbers'], list_index=None, old=20, new=45),
            ],
        ),
        ({'numbers': 20.0}, {'numbers': 20}, []),  # No Diff on float vs int
        (
            {'10': 50}, {'10': 51}, [
                DiffResult(key_list=['10'], list_index=None, old=50, new=51),
            ],
        ),
        (
            {'number_list': [90, 91, 92, 96, 100]}, {'number_list': [90, 91, 92, 93, 94, 100]}, [
                DiffResult(key_list=['number_list'], list_index=3, old=96, new=93),
                DiffResult(key_list=['number_list'], list_index=4, old=100, new=94),
                DiffResult(key_list=['number_list'], list_index=5, old=TrueNull, new=100),
            ],
        ),
        (
            {'missing': {'title': 'hello'}}, {'title': 'hello'}, [
                DiffResult(key_list=['title'], list_index=None, old=TrueNull, new='hello'),
                DiffResult(key_list=['missing', 'title'], list_index=None, old='hello', new=TrueNull),
            ],
        ),
        (
            {'title': 'hello'}, {'added': {'nested': {'title': 'hello'}}}, [
                DiffResult(key_list=['title'], list_index=None, old='hello', new=TrueNull),
                DiffResult(key_list=['added', 'nested', 'title'], list_index=None, old=TrueNull, new='hello'),
            ],
        ),
        (
            {'list': ['acorn', 'tree']}, {'list': ['acorn', 'treenut']}, [
                DiffResult(key_list=['list'], list_index=1, old='tree', new='treenut'),
            ],
        ),
        (
            {'iterable': {'tree', 'acorn'}}, {'iterable': ['tree', 'acorn']}, [
                DiffResult(key_list=['iterable'], list_index=None, old={'tree', 'acorn'}, new=['tree', 'acorn']),
            ],
        ),
        (
            {'nullable': None}, {'nullable': 'Not Null'}, [
                DiffResult(key_list=['nullable'], list_index=None, old=None, new='Not Null'),
            ],
        ),
        (
            {'a': [{'list': 1}, {'list': None}]}, {'a': [{'list': 1}, {'list': 2}]}, [
                DiffResult(key_list=['a', 1, 'list'], list_index=None, old=None, new=2),
            ],
        ),
        (
            {'a': [{'b': [{'c': 1}]}]}, {'a': [{'b': [{'c': 2}]}]}, [
                DiffResult(key_list=['a', 0, 'b', 0, 'c'], list_index=None, old=1, new=2),
            ],
        ),
    ],
)
def test_raw_diff(old_dict, new_dict, expected):
    """Test the low level diff logic."""
    result = _raw_diff(old_dict=old_dict, new_dict=new_dict)

    assert sorted(result) == sorted(expected)


@pytest.mark.parametrize(
    ('old_dict', 'new_dict', 'key_rules'), [
        (
            {'a': {'b': {'c': None}}}, {'a': {'b': {'c': 'Not Null'}}}, [
                KeyRule(pattern=['a', Wildcards.RECURSIVE]),
                KeyRule(pattern=['a', 'b', 'c'], func=check_suppress),
                KeyRule(pattern=['a', Wildcards.SINGLE, Wildcards.SINGLE]),
            ],  # Check Sorting. Only the middle key_rule will suppress the error
        ),
        (
            {'a': [{'b': [{'c': 1}]}]}, {'a': [{'b': [{'c': 2}]}]}, [
                KeyRule(
                    pattern=['a', Wildcards.LIST, 'b', Wildcards.LIST, 'c'],
                    func=check_suppress,
                ),
            ],
        ),
    ],
)
def test_diff_with_rules(old_dict, new_dict, key_rules):
    """Test that the key rules work in various scenarios."""
    result = diff_with_rules(old_dict=old_dict, new_dict=new_dict, key_rules=key_rules)

    assert result == []
    errors = diff_with_rules(old_dict=old_dict, new_dict=new_dict, key_rules=[])
    assert len(errors) == 1
