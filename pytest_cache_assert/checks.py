"""Assertion checks for unit tests."""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

from _pytest.assertion import pytest_assertrepr_compare
from beartype import beartype

from ._check_assert.caching import cache_data, init_cache, load_cached_data
from ._check_assert.constants import DEF_CACHE_DIR_NAME, TEST_DATA_TYPE

# NOTE: additional descriptions for planned features
# - `key_rules`: Dict[str, Optional[Callable[[Any, Any], None]]
#     - (String): rule_callable (ignore, check-likeness, custom)
#         - Specify the key name or pattern of key names using dots for nesting and asterisks for wildcards (jmespath)
#         - The rule callable can be any custom implementation or one of the recommended
#             - The default assertion is an exact match, so any keys not specified here will be checked for exactness
#             - The utility functions provided by the package are for use cases with variable values
#                 - NoOp-ignore field
#                 - Check if null if value is null or check type-of (in-exact)


@beartype
def check_assert(
    test_data: TEST_DATA_TYPE,
    test_dir: Path,
    config: Any,
    *,
    # FIXME: path_cache_file should be discovered through introspection if None
    # TODO: Add `cache_name` / `path_cache_file`: default is test name with `-00#` (or index of parameter). Argument
    #   should accept a static string or custom formatter
    path_cache_file: Optional[Path] = None,
    # TODO: Implement key rules. See notes above. Consider a dataclass KeyRules
    key_rules: Optional[Dict[str, Callable[[Any, Any], None]]] = None,
    # TODO: Implement validator for user customization
    validator: Optional[Callable[[TEST_DATA_TYPE], None]] = None,
    # Pytest Fixture
    cache_assert_config: Optional[Dict[str, str]] = None,
) -> None:
    """Core logic for pytest_cache_assert to handle caching and assertion-checking.

    Args:
        test_data: dictionary to test and/or cache
        test_dir: top-level pytest test directory
        path_cache_file: location of the cache file to write. Default is None and will be resolved through introspection
        key_rules: dictionary of KeyRules too apply for selectively ignoring values
        validator: Custom validation function to be run against the test data before any modification

    Raises:
        AssertionError if any assertion fails.

    """
    # Parse configuration. Set via a custom 'cache_assert_config' module fixture
    cache_assert_config = cache_assert_config or {}
    # > path_cache_dir: location of the cache directory.
    path_cache_dir = test_dir / cache_assert_config.get('rel_path_cache_dir', DEF_CACHE_DIR_NAME)

    validator = validator or (lambda res: res)
    validator(test_data)

    if not path_cache_dir.is_dir():
        init_cache(path_cache_dir)
    if not path_cache_file.is_file():
        # TODO: Generate metadata based on pytest parameters/introspection
        cache_data(path_cache_file, {}, test_data)
    cached_data = load_cached_data(path_cache_file)

    for rule in key_rules or {}:
        # TODO: Move to key_rules to separate function
        #   - Check callable (NoOp ignore; check-likeness; or custom)
        #   - Pop keys from both dictionaries if present
        # test_data = apply_rule(test_data, rule)
        print(rule)

    # TODO: modify the dictionary based on the match precision enum
    # test_data = apply_match_precision(test_data, match_precision)

    # TODO: Consider other functions that might raise an assertion directly with formatting:
    # https://github.com/pytest-dev/pytest/search?l=Python&q=pytest_assertrepr_compare&type=
    # https://github.com/pytest-dev/pytest/search?q=pytest_runtest_protocol
    # https://github.com/pytest-dev/pytest/blob/6247a956010855f227181ba6167c89bb500e9480/src/_pytest/assertion/__init__.py#L115-L168
    # https://github.com/pytest-dev/pytest/blob/dd6d4b2fe0041db3e7a6378a5da67950393053af/src/_pytest/unittest.py#L363-L390
    # https://github.com/pytest-dev/pytest/blob/f28421cc7068b13ba63c1f60cc21f898cccea36c/src/_pytest/runner.py#L110-L115

    error_message = pytest_assertrepr_compare(config, op='==', left=test_data, right=cached_data)
    if error_message:
        raise AssertionError(error_message)
