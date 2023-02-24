"""Pytest Plugin."""

from __future__ import annotations

import inspect
import re
from functools import partial
from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest
from beartype import beartype
from beartype.typing import Any, Callable, Dict, Iterable, Optional, Union
from pydantic import BaseModel

from . import AssertConfig, CacheAssertContainerKeys, main, register, retrieve


class TestMetadata(BaseModel):
    """Test MetaData."""

    test_file: str
    test_name: str
    func_args: Union[Dict, Iterable]  # type: ignore[type-arg]

    class Config:  # noqa: D106
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


_RE_UNSAFE_CHAR = re.compile(r'[/\\]')
"""Used to remove characters from the cache file path that could cause issues."""


@pytest.fixture()
@beartype
def assert_against_cache(
    request: FixtureRequest,
    cache_assert_config: Optional[AssertConfig] = None,
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
    if cache_assert_config:
        register(CacheAssertContainerKeys.CONFIG, cache_assert_config)
    assert_config = retrieve(CacheAssertContainerKeys.CONFIG)

    test_dir = None
    for sub_dir in ['tests', 'test']:
        test_dir = request.config.rootpath / sub_dir
        if test_dir.is_dir():
            break
    else:
        msg = f'Could not locate a "tests/" directory in {test_dir}'
        raise RuntimeError(msg)

    # Read user settings
    path_cache_dir = test_dir / assert_config.cache_dir_rel_path

    # Calculate keyword arguments
    rel_test_file = Path(request.node.fspath).relative_to(test_dir)

    # Escape slashes from the pytest node name
    test_name = _RE_UNSAFE_CHAR.sub('-', request.node.name)
    cache_name = (rel_test_file.parent / rel_test_file.stem / f'{test_name}.json').as_posix()  # noqa: ECE001
    metadata = TestMetadata.from_pytest(request=request, rel_test_file=rel_test_file).dict()

    # FYI: The partial function keyword arguments can be overridden when called
    return partial(main.assert_against_cache, path_cache_dir=path_cache_dir, cache_name=cache_name, metadata=metadata)
