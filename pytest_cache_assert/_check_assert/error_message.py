"""Generate nice error messages."""

from pathlib import Path
from typing import Any, List

from .constants import TEST_DATA_TYPE
from .differ import DiffResult


class RichAssertionError(AssertionError):
    """Custom AssertionError with additional `error_info`."""

    def __init__(self, *args, error_info: Any = None, **kwargs) -> None:
        """Store the error_info for later access."""  # noqa: DAR101
        super(*args, **kwargs)
        self.error_info = error_info


def create(
    test_data: TEST_DATA_TYPE, cached_data: TEST_DATA_TYPE, path_cache_file: Path,
    dict_diff: List[DiffResult],
) -> str:
    """Create the error message.

    Args:
        test_data: the test data
        cached_data: the cached data
        path_cache_file: the path to the cache file
        dict_diff: the diff results

    Returns:
        str: pleasant error message

    """
    return f"""For test data: {test_data}
Found differences with: {path_cache_file}
Differences: {dict_diff}
"""
