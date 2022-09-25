"""tests/test_readme_more.py."""

from contextlib import suppress
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from pytest_cache_assert import AssertRule, Wild, check_suppress, check_type


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
