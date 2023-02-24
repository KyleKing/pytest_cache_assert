"""Check that all imports work as expected in the built package."""

from pprint import pprint

from pytest_cache_assert import AssertRule, check_exact, check_suppress, check_type
from pytest_cache_assert.plugin import assert_against_cache

pprint(locals())  # noqa: T203
