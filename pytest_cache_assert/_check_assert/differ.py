"""Dictionary Differ."""

import dictdiffer
from attrs import Attribute, field, frozen, mutable
from attrs_strict import type_validator
from beartype import beartype
from beartype.typing import Any, Dict, List, Optional, Union

from .constants import DIFF_TYPES, TrueNull, Wildcards
from .key_rules import KeyRule

(_ADD, _REMOVE, _CHANGE) = ('add', 'remove', 'change')
"""Sourced from dictdiffer.

https://github.com/inveniosoftware/dictdiffer/blob/b32e4b0d44b81a6de4cffd7920122c5c96436a79/dictdiffer/__init__.py#L20

"""


@beartype
def _validate_diff_type(_instance: Any, _attribute: Attribute, diff_type: Any) -> None:
    """Validate diff_type.

    Args:
        _instance: instance of a class with `attrs` attributes
        _attribute: Attribute to validate
        diff_type: The value to validate. Expected string diff type label

    Raises:
        ValueError: if diff_type is not an expected type from dictdiffer

    """
    if diff_type not in (_ADD, _REMOVE, _CHANGE):
        raise ValueError(f'Invalid diff_type: {diff_type}')


@frozen(kw_only=True)
class DiffResult:  # noqa: H601
    """Usable Dictionary DIff Result."""

    key_list: List[Union[str, int]] = field(validator=type_validator())
    list_index: Optional[int] = field(validator=type_validator())
    old: DIFF_TYPES = field(validator=type_validator())
    new: DIFF_TYPES = field(validator=type_validator())

    @beartype
    def match_key_pattern(self, pattern: List[Union[str, Wildcards]]) -> bool:
        """Match the provided pattern against the key list. Accepts asterisk wildcards.

        Args:
            pattern: The key pattern to match against. Supports `Wildcards`

        Returns:
            bool: True if the key `pattern` applies to the `key_list`

        """
        if pattern[-1] != Wildcards.RECURSIVE and len(pattern) != len(self.key_list):
            return False

        if Wildcards.RECURSIVE in pattern[:-1]:
            raise ValueError(f'Recursive wildcard can only be used at the end of the pattern: {pattern}')

        @beartype
        def pat_match(pat: Union[str, Wildcards], key: Union[str, int]) -> bool:
            """Attempt to match the pattern against each key."""
            return (  # noqa: DAR101,DAR201
                (key == pat)
                or (pat in {Wildcards.SINGLE, Wildcards.RECURSIVE})
                or (pat == Wildcards.LIST and isinstance(key, int))
            )

        return all(pat_match(pat, key) for key, pat in zip(self.key_list, pattern))


@mutable(kw_only=True)
class DictDiff:  # noqa: H601
    """Mutable data structure to manipulate results of the raw dictdiffer.diff output."""

    # Initial raw output of dictdiffer
    diff_type: str = field(validator=_validate_diff_type)
    raw_keys: Union[str, List[Union[str, int]]] = field(validator=type_validator())
    raw_data: Any

    # Interim Values
    keys: List[Any] = field(factory=list, init=False, validator=type_validator())
    index: Optional[int] = field(default=None, init=False, validator=type_validator())
    data: Any = field(default=None, init=False, validator=type_validator())

    # Final Values
    old: DIFF_TYPES = field(default=TrueNull, init=False)
    new: DIFF_TYPES = field(default=TrueNull, init=False)


# FIXME: Add example of what this is changing. I can't remember why this was necessary
@beartype
def _parse_raw_data_and_raw_keys(diff: DictDiff) -> DictDiff:
    """Handle case where the keys are actually in the data.

    Raises:
        ValueError: on any unexpected states

    """
    diff.data = diff.raw_data
    if diff.raw_keys == '':
        if len(diff.raw_data) != 1:
            raise ValueError(f'Unexpected diff.raw_data from: {diff}')
        inner_list = diff.raw_data[-1]
        diff.raw_keys = inner_list[:-1]
        diff.data = inner_list[-1]
    diff.keys = [diff.raw_keys] if isinstance(diff.raw_keys, str) else [*diff.raw_keys]
    return diff


@beartype
def _parse_data(diff: DictDiff) -> DictDiff:
    """Unwrap additional states of `self.data`.

    Raises:
        ValueError: on any unexpected states

    """
    # Handle case where there was a change in a list and the index is the first value in the data list
    if (
        isinstance(diff.data, list) and len(diff.data) == 1
        and isinstance(diff.data[0], tuple) and len(diff.data[0]) == 2
    ):
        diff.keys.append(diff.data[0][0])
        diff.data = diff.data[0][1]
    # Handle case where the data is a new dictionary that has keys that should be in keys
    while isinstance(diff.data, dict):
        items = [*diff.data.items()]
        if len(items) != 1:
            raise ValueError(f'Unexpected diff.data from: {diff}')
        key, value = items[0]
        diff.keys.append(key)
        diff.data = value
    return diff


@beartype
def _parse_keys(diff: DictDiff) -> DictDiff:
    """Parse the key list from `dictdiffer.diff`."""
    last_key = diff.keys[-1] if diff.keys else None
    if isinstance(last_key, int):
        # Extract the last key as the index if an integer
        diff.keys = diff.keys[:-1]
        diff.index = last_key
    return diff


@beartype
def _assign_old_and_new(diff: DictDiff) -> DictDiff:
    """Assign new and old data based on the type of diff.

    Raises:
        ValueError: on any unexpected states

    """
    if diff.diff_type == _ADD:
        diff.new = diff.data
    elif diff.diff_type == _REMOVE:
        diff.old = diff.data
    elif diff.diff_type == _CHANGE:
        if len(diff.data) != 2:
            raise ValueError(f'Unexpected diff.data from: {diff}')
        diff.old = diff.data[0]
        diff.new = diff.data[1]
    else:  # Shouldn't be reachable because of validator
        raise ValueError(f'Unknown diff.diff_type from: {diff}')
    return diff


@beartype
def get_diff_result(diff: DictDiff) -> DiffResult:
    """Generate the diff_result from parsed data.

    Returns:
        DiffResult: The diff_result

    """
    diff = _parse_raw_data_and_raw_keys(diff)
    diff = _assign_old_and_new(_parse_keys(_parse_data(diff)))
    return DiffResult(key_list=diff.keys, list_index=diff.index, old=diff.old, new=diff.new)


@beartype
def _raw_diff(*, old_dict: DIFF_TYPES, new_dict: Dict[str, Any]) -> List[DiffResult]:
    """Determine the differences between two dictionaries.

    Args:
        old_dict: old dictionary (typically cached one)
        new_dict: new dictionary (typically test data)

    Returns:
        List[DiffResult]: list of DiffResult objects

    """
    results = []
    raw_diff = dictdiffer.diff(first=old_dict, second=new_dict, expand=True, dot_notation=False)
    for (_type, _keys, _data) in raw_diff:
        dict_diff = DictDiff(diff_type=_type, raw_keys=_keys, raw_data=_data)
        diff_result = get_diff_result(dict_diff)
        results.append(diff_result)

    return results


@beartype
def diff_with_rules(*, old_dict: DIFF_TYPES, new_dict: DIFF_TYPES, key_rules: List[KeyRule]) -> List[DiffResult]:
    """Determine the differences between two dictionaries.

    FYI: Sorts by specificity so that more specific key_rules apply over less specific ones

    Args:
        old_dict: old dictionary (typically cached one)
        new_dict: new dictionary (typically test data)
        key_rules: list of key rules to ignore certain differences

    Returns:
        List[DiffResult]: list of DiffResult objects

    """
    @beartype
    def matched_rule(diff_result: DiffResult) -> bool:
        """Return `False` if the difference should be suppressed."""
        for rule in sorted(key_rules, key=lambda _rule: str(_rule.pattern)):  # noqa: DAR101, DAR201
            if diff_result.match_key_pattern(rule.pattern):
                return rule.func(old=diff_result.old, new=diff_result.new)
        return False

    return [_d for _d in _raw_diff(old_dict=old_dict, new_dict=new_dict) if not matched_rule(_d)]
