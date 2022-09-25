"""Test example code for the README file."""

import sys
from datetime import datetime

import pytest
from beartype import beartype
from beartype.typing import Dict, List, Optional
from pydantic import BaseModel


class User(BaseModel):  # noqa: H601
    """Example from pydantic documentation."""

    id: int  # noqa: A003,VNE003
    name = 'John Doe'
    signup_ts: Optional[datetime] = None
    friends: List[int] = []


@beartype
def create_data(name: str) -> Dict:
    """Arbitrary function that returns a dictionary.

    This demonstration uses pydantic, but any dictionary can be tested!

    """
    return User(id=sys.maxsize, name=name).dict()


@pytest.mark.parametrize('name', ['Test Name 1', 'Test Name 2'])
def test_create_data(name, assert_against_cache):
    """Basic test of create_data()."""
    result = create_data(name=name)

    # One could manually create the expected dictionary
    cache = {'id': 9223372036854775807, 'signup_ts': None, 'friends': [], 'name': name}
    assert result == cache
    # ----------------------------------------------------------------------------------
    # Or utilize the pytest_cache_assert fixture to compare against the last cached version
    assert_against_cache(result)
