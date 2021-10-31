"""Key Rules."""

from typing import Callable, List

import attr
from attrs_strict import type_validator

from .constants import DIFF_TYPES

# NOTE: additional descriptions for planned features
# - `key_rules`: Dict[str, Optional[Callable[[Any, Any], None]]
#     - (String): rule_callable (ignore, check-likeness, custom)
#         - Specify the key name or pattern of key names using dots for nesting and asterisks for wildcards (jmespath)
#         - The rule callable can be any custom implementation or one of the recommended
#             - The default assertion is an exact match, so any keys not specified here will be checked for exactness
#             - The utility functions provided by the package are for use cases with variable values
#                 - NoOp-ignore field
#                 - Check if null if value is null or check type-of (in-exact)


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class KeyRule:  # noqa: H601
    """Key Rule."""

    key_list: List[str] = attr.ib(validator=type_validator())
    func: Callable[[DIFF_TYPES], bool] = attr.ib(validator=type_validator())
