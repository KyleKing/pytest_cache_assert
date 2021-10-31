"""Assertion checks for unit tests.

FYI: Should not require any pytest functionality

"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

import dictdiffer
from beartype import beartype

from ._check_assert.caching import cache_data, init_cache, load_cached_data
from ._check_assert.constants import TEST_DATA_TYPE

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
def assert_against_cache(
    test_data: TEST_DATA_TYPE,
    path_cache_dir: Path,
    cache_name: str,
    # FIXME: Implement key rules. See notes above. Consider a dataclass KeyRules
    key_rules: Optional[Dict[str, Callable[[Any, Any], None]]] = None,
    validator: Optional[Callable[[TEST_DATA_TYPE], None]] = None,
    metadata: Optional[dict] = None,
) -> None:
    """Core logic for pytest_cache_assert to handle caching and assertion-checking.

    Args:
        test_data: dictionary to test and/or cache
        path_cache_dir: location of the cache directory
        cache_name: relative string path from the test_dir to the JSON cache file
        key_rules: dictionary of KeyRules too apply for selectively ignoring values
        validator: Custom validation function to be run against the test data before any modification
        metadata: metadata dictionary to store in the cache file

    Raises:
        AssertionError if any assertion fails

    """
    validator = validator or (lambda _res: None)
    validator(test_data)

    path_cache_file = path_cache_dir / cache_name
    if not path_cache_dir.is_dir():
        init_cache(path_cache_dir)
    # TODO: Always write metadata. Edge case is if multiple tests use the same cache file
    #   Will merge the metadata to show values as sets
    if not path_cache_file.is_file():
        cache_data(path_cache_file, metadata or {}, test_data)
    cached_data = load_cached_data(path_cache_file)

    for rule in key_rules or {}:
        # TODO: Move to key_rules to separate function
        #   - Check callable (NoOp ignore; check-likeness; or custom)
        #   - Pop keys from both dictionaries if present
        # test_data = apply_rule(test_data, rule)
        print(rule)

    dict_diff = [*dictdiffer.diff(test_data, cached_data)]
    if dict_diff:
        # TODO: pretty print the dictionaries and "textwrap" to terminal width? (Move to dedicated function)
        raise AssertionError(f"""For test data: {test_data}
Found differences with: {path_cache_file}
Differences: {dict_diff}
""")
