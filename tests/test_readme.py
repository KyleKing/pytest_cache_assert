"""Test example code for the README file."""

import sys
from datetime import datetime
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
    return User(id=sys.maxsize, name=name).json()


@pytest.mark.parametrize('name', ['Test Name 1', 'Test Name 2'])
def test_create_data(name):
    """Basic test of create_data()."""
    # One could manually create the expected dictionary
    cache = {'id': 9223372036854775807, 'signup_ts': None, 'friends': [], 'name': 'Test Name 1'}
    assert create_data(name=name) == cache
    # Or use the pytest_cache_assert function to compare against the last recorded dictionary
    assert check_assert(create_data(name=name))
