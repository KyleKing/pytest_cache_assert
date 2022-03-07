"""Generate nice error messages."""

from pathlib import Path

from beartype.typing import Any, List

from .differ import DiffResult


class RichAssertionError(AssertionError):
    """Custom AssertionError with additional `error_info`."""

    def __init__(self, *args, error_info: Any = None) -> None:
        """Store the error_info for later access."""  # noqa: DAR101
        super().__init__(*args)
        self.error_info = error_info

    @classmethod
    def create_message(
        cls, test_data: Any, cached_data: Any, path_cache_file: Path,
        diff_results: List[DiffResult],
    ) -> str:
        """Create the error message.

        Args:
            test_data: the test data
            cached_data: the cached data
            path_cache_file: the path to the cache file
            diff_results: the diff results

        Returns:
            str: pleasant error message

        """
        # PLANNED: Cap length of error message. There might be a library that can help with that
        return f"""For test data: {test_data}
Found differences with: {path_cache_file}
Differences: {diff_results}
"""
