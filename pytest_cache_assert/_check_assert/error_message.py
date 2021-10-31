"""Generate nice error messages."""

from pathlib import Path
from typing import List

from .constants import TEST_DATA_TYPE
from .differ import DiffResult


def create(test_data: TEST_DATA_TYPE, cached_data: TEST_DATA_TYPE, path_cache_file: Path,
           dict_diff: List[DiffResult]) -> str:
    """Create the error message.


    """
    # TODO: pretty print the dictionaries and "textwrap" to terminal width?
    return f"""For test data: {test_data}
Found differences with: {path_cache_file}
Differences: {dict_diff}
"""
