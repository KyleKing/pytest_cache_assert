"""Test example code for the README file."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
from beartype import beartype
from pydantic import BaseModel

from pytest_cache_assert import check_assert


class User(BaseModel):  # noqa: H601
    """Example from pydantic documentation."""

    id: int  # noqa: A003,VNE003
    name = 'John Doe'
    signup_ts: Optional[datetime] = None
    friends: List[int] = []


@beartype
def create_data(name: str) -> Dict[str, Any]:
    """Arbitrary function that returns a dictionary.

    This demonstration uses pydantic, but any dictionary can be tested!

    """
    return User(id=sys.maxsize, name=name).dict()


@pytest.mark.parametrize('name', ['Test Name 1', 'Test Name 2'])
def test_create_data(name):
    """Basic test of create_data()."""
    result = create_data(name=name)

    # One could manually create the expected dictionary
    cache = {'id': 9223372036854775807, 'signup_ts': None, 'friends': [], 'name': name}
    assert result == cache
    # Or use the pytest_cache_assert function to compare against the last recorded dictionary
    # PLANNED: This logic should be implemented through introspection and not in the test code each time!!
    parameter_index = int(name[-1]) - 1
    path_test_file = Path(__file__).resolve()
    path_cache_dir = path_test_file.parent / 'assert-cache'
    check_assert(
        result,
        path_cache_dir / f'{path_test_file.stem}/test_create_data-{parameter_index:3}.json',
        path_cache_dir,
    )
