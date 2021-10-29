"""Assertion checks for unit tests."""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

from _check_assert.caching import cache_data, init_cache, load_cached_data
from _check_assert.constants import TEST_DATA_TYPE, MatchPrecision
from beartype import beartype

# NOTE: additional descriptions for planned features
# - `key_rules`: Dict[str, Optional[Callable[[Any, Any], None]]
#     - (String): rule_callable (ignore, check-likeness, custom)
#         - Specify the key name or pattern of key names using dots for nesting and asterisks for wildcards (jmespath)
#         - The rule callable can be any custom implementation or one of the recommended
#             - The default assertion is an exact match, so any keys not specified here will be checked for exactness
#             - The utility functions provided by the package are for use cases with variable values
#                 - NoOp-ignore field
#                 - Check if null if value is null or check type-of (in-exact)
# - transformer: custom serializer of Dict[str, Union[str, dict]]. Could use cattrs, marshmallow, Pydantic, or some
#  custom function as long as the result is a dict
#     - Can be used for additional checks with Cerberus or other library (custom_validator)
# -->


@beartype
def check_assert(
    test_data: TEST_DATA_TYPE,
    *,
    # FIXME: path_cache_file should be discovered through introspection if None
    # TODO: Add `cache_name` / `path_cache_file`: default is test name with `-00#` (or index of parameter). Argument
    #   should accept a static string or custom formatter
    path_cache_file: Path,
    # FIXME: path_cache_dir should be set globally or use a default. Not in-test-specified
    path_cache_dir: Path,
    # TODO: Implement match_precision
    match_precision: MatchPrecision = MatchPrecision.EXACT,
    # TODO: Implement key rules. See notes above
    key_rules: Optional[Dict[str, Callable[[Any, Any], None]]] = None,
    # TODO: Implement transformer (deserialization) and validator for user customization
    validator: Optional[Callable[[TEST_DATA_TYPE], None]] = None,
    transformer: Optional[Callable[[TEST_DATA_TYPE], Any]] = None,
) -> None:
    """Core logic for pytest_cache_assert to handle caching and assertion-checking.

    Will raise AssertionError if any assertion fails.

    Args:
        test_data: dictionary to test and/or cache
        path_cache_file: location of the cache file to write. Default is None and will be resolved through introspection
        path_cache_dir: location of the cache directory.

    """
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

    transformer = transformer or (lambda res: res)
    assert transformer(test_data) == cached_data  # noqa: B101,S101
