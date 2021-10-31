"""Dictionary Differ."""

from typing import List, Optional, Tuple, Union

import attr
import dictdiffer
from attrs_strict import type_validator
from beartype import beartype

from .constants import DIFF_TYPES, TrueNull
from .key_rules import KeyRule

(_ADD, _REMOVE, _CHANGE) = ('add', 'remove', 'change')
"""Sourced from dictdiffer.

https://github.com/inveniosoftware/dictdiffer/blob/b32e4b0d44b81a6de4cffd7920122c5c96436a79/dictdiffer/__init__.py#L20

"""


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class DiffResult:  # noqa: H601
    """Usable Dictionary DIff Result."""

    key_list: List[str] = attr.ib(validator=type_validator())
    list_index: Optional[int] = attr.ib(validator=type_validator())
    old: DIFF_TYPES = attr.ib(validator=type_validator())
    new: DIFF_TYPES = attr.ib(validator=type_validator())

    def match_key_pattern(self, pattern: List[str]) -> bool:
        """Match the provided pattern against the key list. Accepts asterisk wildcards.

        Args:
            pattern: The key pattern to match against

        Returns:
            bool: True if the key `pattern` applies to the `key_list`

        """
        if len(pattern) != len(self.key_list):
            return False

        return all(pat == '*' or key == pat for key, pat in zip(self.key_list, pattern))


@beartype
def _parse_keys(raw_keys: List[Union[str, int]]) -> Tuple[List[str], Optional[int]]:
    """Parse the key list from dictdiffer for DiffResult.

    Args:
        raw_keys: list of keys that may contain dot-syntax

    Returns:
        Tuple: the complete list of keys and the optional list index if relevant

    """
    key_list = []
    index = None
    for key in raw_keys:
        if isinstance(key, int) and key == raw_keys[-1]:
            index = key
            break
        key_list.extend(key.split('.') if '.' in key else [key])

    return (key_list, index)


@beartype
def _raw_diff(*, old_dict: dict, new_dict: dict) -> List[DiffResult]:
    """Determine the differences between two dictionaries.

    Args:
        old_dict: old dictionary (typically cached one)
        new_dict: new dictionary (typically test data)

    Returns:
        List[DiffResult]: list of DiffResult objects

    Raises:
        ValueError: on any unexpected states

    """
    # TODO: Refactor into smaller functions!
    results = []
    for (diff_type, keys, data) in dictdiffer.diff(old_dict, new_dict):
        # Handle case where the keys are actually in the data
        if keys == '':
            if len(data) != 1:
                raise ValueError(f'Unexpected data: {(diff_type, keys, data)} for {(old_dict, new_dict)}')
            inner_list = data[-1]
            keys = inner_list[:-1]
            data = inner_list[-1]
        keys = [keys] if isinstance(keys, str) else [*keys]
        # Handle case where there was a change in a list and the index is the first value in the data list
        if isinstance(data, list) and len(data) == 1 and isinstance(data[0], tuple) and len(data[0]) == 2:
            keys.append(data[0][0])
            data = data[0][1]
        # Handle case where the data is a new dictionary that has keys that should be in keys
        while isinstance(data, dict):
            items = [*data.items()]
            if len(items) != 1:
                raise ValueError(f'Unexpected data: {(diff_type, keys, data)} for {(old_dict, new_dict)}')
            key, value = items[0]
            keys.append(key)
            data = value
        # Calculate the list_index and key list
        key_list, list_index = _parse_keys(keys)

        # Assign new and old data based on the type of diff
        old, new = TrueNull, TrueNull
        if diff_type == _ADD:
            new = data
        elif diff_type == _REMOVE:
            old = data
        elif diff_type == _CHANGE:
            if len(data) != 2:
                raise ValueError(f'Unexpected data: {(diff_type, keys, data)} for {(old_dict, new_dict)}')
            old = data[0]
            new = data[1]
        else:
            raise ValueError(f'Unknown diff type: {diff_type}')

        diff_result = DiffResult(key_list=key_list, list_index=list_index, old=old, new=new)
        results.append(diff_result)

    return results


@beartype
def diff_with_rules(*, old_dict: dict, new_dict: dict, key_rules: List[KeyRule]) -> List[DiffResult]:
    """Determine the differences between two dictionaries.

    Args:
        old_dict: old dictionary (typically cached one)
        new_dict: new dictionary (typically test data)
        key_rules: list of key rules to ignore certain differences

    Returns:
        List[DiffResult]: list of DiffResult objects

    """
    return [
        any(rule.func(old=_d.old, new=_d.new) for rule in key_rules if _d.match_key_pattern(rule.key_list))
        for _d in _raw_diff(old_dict=old_dict, new_dict=new_dict)
    ]
