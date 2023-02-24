"""Generate nice error messages."""

from pathlib import Path
from pprint import pformat

from beartype import beartype
from beartype.typing import Any

from .differ import DiffResults


class NoCacheError(FileNotFoundError):
    """Custom Assertion when no cached data is available for read."""

    @beartype
    def __init__(self, path_cache_file: Path) -> None:
        super().__init__(f'No cache for: {path_cache_file}')


class RichAssertionError(AssertionError):
    """Custom AssertionError with additional `error_info`."""

    def __init__(self, *args: Any, error_info: Any = None) -> None:
        """Store the error_info for later access."""  # noqa: DAR101
        super().__init__(*args)
        self.error_info = error_info

    @classmethod
    @beartype
    def create_message(
        cls,
        test_data: Any,   # noqa: ARG003
        cached_data: Any,  # noqa: ARG003
        path_cache_file: Path,
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
        @beartype
        def fmt_line(prefix: str, data: Any) -> str:
            indented_data = ('\n' + ' ' * len(prefix)).join(pformat(data).split('\n'))
            return f'{prefix}{indented_data}'

        diff_prefix = '> Differences: '
        line_diff = fmt_line(diff_prefix, diff_results.to_dict())
        file_diff = f'\n> Found differences with: {path_cache_file}' if path_cache_file else ''
        return f'{file_diff}\n{line_diff}\n'
