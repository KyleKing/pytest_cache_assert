"""Test example code for the README file."""

import sys
from contextlib import suppress
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from beartype import beartype
from beartype.typing import Any, Dict, List, Optional
from pydantic import BaseModel

from pytest_cache_assert import AssertRule, Wild, check_suppress, check_type


class User(BaseModel):  # noqa: H601
    """Example from pydantic documentation."""

    id: int  # noqa: A003,VNE003
    name = 'John Doe'
    signup_ts: Optional[datetime] = None
    friends: List[int] = []


@beartype
def create_data(name: str) -> Dict[str, Any]:
    """Arbitrary function that returns a dictionary.

    This demonstration uses pydantic, but any dictionary can be tested!

    """
    return User(id=sys.maxsize, name=name).dict()


@pytest.mark.parametrize('name', ['Test Name 1', 'Test Name 2'])
def test_create_data(name, assert_against_cache):
    """Basic test of create_data()."""
    result = create_data(name=name)

    # One could manually create the expected dictionary
    cache = {'id': 9223372036854775807, 'signup_ts': None, 'friends': [], 'name': name}
    assert result == cache
    # ----------------------------------------------------------------------------------
    # Or utilize the pytest_cache_assert fixture to compare against the last cached version
    assert_against_cache(result)


def test_assert_against_cache_key_rules(assert_against_cache):
    """Demonstrate use of `assert_rules`."""
    now = datetime.now()
    cached_data = {
        'date': str(now),
        'nested': {'uuid': str(uuid4())},
        'ignored': {'a': 1, 'b': 2},
        # 'ignored_within_list': [{'a': 1}, {'b': 2}],
        # TODO: Added/remove field, etc.
    }
    test_data = {
        'date': str(now + timedelta(hours=3)),
        'nested': {'uuid': str(uuid4())},
        'ignored': {'recursively': {'a': {'b': {'c': 1}}}},
        # 'ignored_within_list': [{'a': 1}, {'b': 2}],
    }
    with suppress(AssertionError):
        # Ensures that the cache file has been created
        assert_against_cache(cached_data)

    assert_rules = [
        # To ignore values for 'ignored.a' and 'ignored.b', create a rule
        #   Here, we use the wildcard for dictionary keys
        AssertRule.build_re(pattern=['ignored', Wild.keys()], func=check_suppress),
        AssertRule.build_re(pattern=['ignored', Wild.keys(2)], func=check_suppress),

        # Instead of suppressing, the type of data could be resolved and compared
        #   This is useful for datetime or UUID values where we expect variability
        AssertRule(pattern='date', func=check_type),
        AssertRule.build_re(pattern=['nested', 'uuid'], func=check_type),

        # Any "func" with arguments 'old' and 'new' can be used as a rule
    ]

    # Without assert rules, an AssertionError is raised
    with pytest.raises(AssertionError):
        assert_against_cache(test_data)
    # But, with the custom logic, the cache assertion check will succeed
    assert_against_cache(test_data, assert_rules=assert_rules)
