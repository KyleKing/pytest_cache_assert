"""Dictionary Differ."""

from contextlib import suppress

from beartype import beartype
from beartype.typing import Dict, List
from deepdiff import DeepSearch, extract
from deepdiff.diff import DeepDiff
from pydantic import BaseModel

from .assert_rules import AssertRule
from .constants import DIFF_TYPES, NotFound


class DiffResults(BaseModel):
    """Result from calculating the diff."""

    results: Dict

    @beartype
    def to_dict(self) -> Dict:
        return self.results

    @beartype
    def append(self, assert_rule: AssertRule, result: Dict) -> None:
        self.results[f'For {assert_rule}'] = result


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
def diff_with_rules(*, old_dict: DIFF_TYPES, new_dict: DIFF_TYPES, assert_rules: List[AssertRule]) -> DiffResults:
    """Determine the differences between two dictionaries.

    Args:
        old_dict: old dictionary (typically cached one)
        new_dict: new dictionary (typically test data)
        assert_rules: list of key rules to ignore certain differences

    Returns:
        DiffResults: Diff Object

    """
    key_str = 'str'
    key_re = 'regex'
    collector = {key_str: [], key_re: []}
    for ar in assert_rules:
        collector[key_re if ar.is_regex else key_str].append(ar.pattern)

    diff_result = _raw_diff(
        old_dict=old_dict,
        new_dict=new_dict,
        exclude_paths=collector[key_str],
        exclude_regex_paths=collector[key_re],
    )

    for ar in assert_rules:
        paths = []
        for data_set in [old_dict, new_dict]:
            ds = DeepSearch(data_set, ar.pattern, use_regexp=ar.is_regex)
            paths.extend([*ds.get('matched_paths', {})])
        for pth in set(paths):
            new_value, old_value = NotFound(), NotFound()
            with suppress(KeyError):
                old_value = extract(old_dict, pth)
            with suppress(KeyError):
                new_value = extract(new_dict, pth)
            if not ar.func(old_value, new_value):
                diff_result.append(ar, {'old_value': old_value, 'new_value': new_value})

    return diff_result
