"""Pytest Plugin."""


from __future__ import annotations

import inspect
from functools import partial
from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest
from beartype import beartype
from beartype.typing import Any, Callable, Dict, Iterable, Optional, Union
from pydantic import BaseModel

from . import AssertConfig, main


class TestMetadata(BaseModel):
    """Test MetaData."""

    test_file: str
    test_name: str
    func_args: Union[Dict, Iterable]  # type: ignore[type-arg]

    class Config:
        arbitrary_types_allowed = True
        frozen = True

    @classmethod
    @beartype
    def from_pytest(cls, request: FixtureRequest, rel_test_file: Path) -> TestMetadata:
        """Resolve TestMetadata.

        Args:
            request: pytest fixture used to identify the test directory
            rel_test_file: relative path to the test file

        Returns:
            TestMetadata: new TestMetadata

        """
        test_name = (f'{request.cls.__name__}/' if request.cls else '') + request.node.originalname
        test_params = [*inspect.signature(request.node.function).parameters.keys()]
        func_args = {key: value for key, value in request.node.funcargs.items() if key in test_params}
        return cls(test_file=rel_test_file.as_posix(), test_name=test_name, func_args=func_args)


@pytest.fixture()
@beartype
def cache_assert_config() -> AssertConfig:
    """Configure pytest_cache_assert using `AssertConfig`."""
    return AssertConfig()


@pytest.fixture()
@beartype
def assert_against_cache(
    request: FixtureRequest,
    cache_assert_config: Optional[AssertConfig],
) -> Callable[[Any], None]:
    """Return main.assert_against_cache with pytest-specific arguments already specified.

    Args:
        request: pytest fixture used to identify the test directory
        cache_assert_config: pytest fixture that returns AssertConfig for user configuration

    Returns:
        Callable[[Any], None]: `main.assert_against_cache()` with test_dir already specified

    Raises:
        RuntimeError: if the test directory cannot be determined

    """
    cache_assert_config = cache_assert_config or AssertConfig()

    test_dir = None
    for sub_dir in ['tests', 'test']:
        test_dir = request.config.rootpath / sub_dir
        if test_dir.is_dir():
            break
    else:
        raise RuntimeError(f'Could not locate a "tests/" directory in {test_dir}')

    # Read user settings
    path_cache_dir = test_dir / cache_assert_config.cache_dir_rel_path

    # Calculate keyword arguments
    rel_test_file = Path(request.node.fspath).relative_to(test_dir)

    cache_name = (rel_test_file.parent / rel_test_file.stem / f'{request.node.name}.json').as_posix()  # noqa: ECE001
    metadata = TestMetadata.from_pytest(request=request, rel_test_file=rel_test_file).dict()

    # FYI: The partial function keyword arguments can be overridden when called
    return partial(main.assert_against_cache, path_cache_dir=path_cache_dir, cache_name=cache_name, metadata=metadata)
