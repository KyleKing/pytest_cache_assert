"""Check that all imports work as expected.

Primarily checking that:

1. No optional dependencies are required

FIXME: Replace with programmatic imports? Maybe explicit imports to check backward compatibility of public API?
    https://stackoverflow.com/questions/34855071/importing-all-functions-from-a-package-from-import

"""

from pytest_cache_assert import AssertRule, check_exact, check_suppress, check_type  # noqa: F401
from pytest_cache_assert.plugin import assert_against_cache  # noqa: F401
