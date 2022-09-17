"""Dictionary Differ."""

from contextlib import suppress

from beartype import beartype
from beartype.typing import Dict, List
from deepdiff import DeepSearch, extract
from deepdiff.diff import DeepDiff
from pydantic import BaseModel

from .constants import DIFF_TYPES
from .key_rules import KeyRule


class DiffResults(BaseModel):
    """Result from calculating the diff."""

    results: Dict

    @beartype
    def to_dict(self) -> Dict:
        return self.results

    @beartype
    def append(self, key_rule: KeyRule, result: Dict) -> None:
        self.results[f'For {key_rule}'] = result


@beartype
def _raw_diff(*, old_dict: DIFF_TYPES, new_dict: DIFF_TYPES, **diff_kwargs) -> DiffResults:
    """Determine the differences between two dictionaries.

    Args:
        old_dict: old dictionary (typically cached one)
        new_dict: new dictionary (typically test data)
        diff_kwargs: pass-through arguments to DeepDiff

    Returns:
        DiffResults: Diff Object

    """
    return DiffResults(results=DeepDiff(t1=old_dict, t2=new_dict, **diff_kwargs))


@beartype
def diff_with_rules(*, old_dict: DIFF_TYPES, new_dict: DIFF_TYPES, key_rules: List[KeyRule]) -> DiffResults:
    """Determine the differences between two dictionaries.

    Args:
        old_dict: old dictionary (typically cached one)
        new_dict: new dictionary (typically test data)
        key_rules: list of key rules to ignore certain differences

    Returns:
        DiffResults: Diff Object

    """
    # FIXME: Move to KeyRules? (is_regex?)
    key_str = 'str'
    key_pat = 'Pattern'
    collector = {key_str: [], key_pat: []}
    for kr in key_rules:
        collector[key_str if isinstance(kr.pattern, str) else key_pat].append(kr.pattern)

    diff_result = _raw_diff(
        old_dict=old_dict,
        new_dict=new_dict,
        exclude_paths=collector[key_str],
        exclude_regex_paths=collector[key_pat],
    )

    for kr in key_rules:
        paths = []
        for data_set in [old_dict, new_dict]:
            ds = DeepSearch(data_set, kr.pattern, use_regexp=not isinstance(kr.pattern, str))
            paths.extend([*ds.get('matched_paths', {})])
        for pth in set(paths):
            with suppress(KeyError):  # FIXME: Use new <Missing> Class if not found!
                old_value = extract(old_dict, pth)
                new_value = extract(new_dict, pth)
                if not kr.func(old_value, new_value):
                    diff_result.append(kr, {'old_value': old_value, 'new_value': new_value})

    return diff_result
