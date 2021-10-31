
"""Check that all imports work as expected.

Primarily checking that:

1. No optional dependencies are required

"""

from pytest_cache_assert import KeyType, check_exact, check_suppress, check_type
from pytest_cache_assert.plugin import assert_against_cache
