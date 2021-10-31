"""Dictionary Differ."""

from typing import List, Optional

import attr
import dictdiffer
from attrs_strict import type_validator
from beartype import beartype

from .constants import _DIFF_TYPES
from .key_rules import KeyRule


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class DiffResult:  # noqa: H601
    """Usable Dictionary DIff Result."""

    key_list: List[str] = attr.ib(validator=type_validator())
    list_index: Optional[int] = attr.ib(validator=type_validator())
    old: _DIFF_TYPES = attr.ib(validator=type_validator())
    new: _DIFF_TYPES = attr.ib(validator=type_validator())

    def match_key_pattern(self, pattern: List[str]) -> bool:
        """Match the provided pattern against the key list. Accepts asterisk wildcards."""
        if len(pattern) != len(self.key_list):
            return False

        return all(pat == '*' or key == pat for key, pat in zip(self.key_list, pattern))


(_ADD, _REMOVE, _CHANGE) = ('add', 'remove', 'change')
"""Sourced from dictdiffer.

https://github.com/inveniosoftware/dictdiffer/blob/b32e4b0d44b81a6de4cffd7920122c5c96436a79/dictdiffer/__init__.py#L20

"""


@beartype
def _raw_diff(*, old: dict, new: dict) -> List[DiffResult]:
    """Determine the differences between two dictionaries."""
    results = []
    for dict_diff in dictdiffer.diff(old, new):
        results.append(DiffResult(key_list=[], list_index=None, old=None, new=None))

    return results


@beartype
def diff(*, old: dict, new: dict, key_rules: List[KeyRule]) -> dict:
    """Determine the differences between two dictionaries."""
    dict_diff = {}
    untested_rules = [*key_rules.keys()]
    for _diff in _raw_diff(old=old, new=new):
        # PLANNED: pop rules that have been used
        for rule in untested_rules:
            # TODO: Move to key_rules to separate function
            #   - Check callable (NoOp ignore; check-likeness; or custom)
            #   - Pop keys from both dictionaries if present
            # test_data = apply_rule(test_data, rule)
            pass

        dict_diff.append(_diff)
    return dict_diff
