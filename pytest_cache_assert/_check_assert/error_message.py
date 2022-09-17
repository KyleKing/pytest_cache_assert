"""Generate nice error messages."""

from pathlib import Path
from pprint import pformat

from beartype.typing import Any

from .differ import DiffResults


class NoCacheError(FileNotFoundError):
    """Custom Assertion when no cached data is available for read."""

    ...


class RichAssertionError(AssertionError):
    """Custom AssertionError with additional `error_info`."""

    def __init__(self, *args, error_info: Any = None) -> None:
        """Store the error_info for later access."""  # noqa: DAR101
        super().__init__(*args)
        self.error_info = error_info

    @classmethod
    def create_message(
        cls, test_data: Any, cached_data: Any, path_cache_file: Path,
        diff_results: DiffResults,
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
        return f"""
> For test data: {pformat(test_data)}
> Found differences with: {path_cache_file}
> Differences: {diff_results.to_dict()}
"""
