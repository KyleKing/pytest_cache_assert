"""Test example code for the README file."""

import re
import sys
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from beartype import beartype
from beartype.typing import Any, Dict, List, Optional
from pydantic import BaseModel

from pytest_cache_assert import AssertRule, check_suppress, check_type


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


# FIXME: The README example doesn't work and could be improved...
@pytest.mark.skip('FIXME: Update this test and the associated README...')
def test_assert_against_cache_key_rules(assert_against_cache):
    """Demonstrate use of `assert_rules`."""
    now = datetime.now()
    cached_data = {
        'date': str(now),
        'nested': {'uuid': str(uuid4())},
        'ignored': {'a': 1, 'b': 2},
    }
    test_data = {
        'date': str(now + timedelta(hours=3)),
        'nested': {'uuid': str(uuid4())},
        'ignored': {'recursively': {'a': {'b': {'c': 1}}}},
    }

    assert_rules = [
        # Suppress keys 'ignored.a' and 'ignored.b' with the SINGLE wildcard,
        #   which aren't present in the test-data and would otherwise error
        AssertRule(pattern=['ignored', 'Wildcards.SINGLE'], func=check_suppress),  # TODO: ???
        # The pattern can also recursively apply to data below
        AssertRule(
            pattern=re.compile('ignored.+recursively.+'),
            func=check_suppress,
        ),
        # Instead of suppressing, the type can be coerced from the string and verified
        #   This is useful for datetime or UUID's where the string will be different,
        #   but both values are the same type
        AssertRule(pattern='date', func=check_type),
        AssertRule(pattern="root['nested']['uuid']", func=check_type),
        # Custom functions can also be specified to check a datetime format, etc.
        #   The function must accept the keyword arguments 'old' and 'new'
    ]

    # In this example, the cache file has been deleted, so first call will recreate it
    assert_against_cache(cached_data)
    # Then this line demonstrates that assert_rules will suppress the errors
    assert_against_cache(test_data, assert_rules=assert_rules)

    # While without key rules, an AssertionError is raised
    with pytest.raises(AssertionError):
        assert_against_cache(test_data)
