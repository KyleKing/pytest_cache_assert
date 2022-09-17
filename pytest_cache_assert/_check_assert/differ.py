"""Dictionary Differ."""

from beartype import beartype
from beartype.typing import Dict, List
from deepdiff.diff import DeepDiff
from pydantic import BaseModel

from .constants import DIFF_TYPES
from .key_rules import KeyRule


class DiffResults(BaseModel, frozen=True):
    """Result from calculating the diff."""

    results: Dict

    @beartype
    def to_dict(self) -> Dict:
        return self.results


@beartype
def _raw_diff(*, old_dict: DIFF_TYPES, new_dict: DIFF_TYPES) -> DiffResults:
    """Determine the differences between two dictionaries.

    Args:
        old_dict: old dictionary (typically cached one)
        new_dict: new dictionary (typically test data)

    Returns:
        DiffResults: Diff Object

    """
    return DiffResults(results=DeepDiff(t1=old_dict, t2=new_dict))


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
    return _raw_diff(old_dict=old_dict, new_dict=new_dict)
