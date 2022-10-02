"""Test serialization."""

import json
from functools import partial
from unittest.mock import MagicMock
from uuid import UUID

import arrow
import pytest

from pytest_cache_assert._check_assert.serializer import make_diffable


@pytest.mark.parametrize(
    ('value', 'expected'), [
        ('20211101', '20211101'),
        (arrow.get('20211101'), '2021-11-01T00:00:00+00:00'),
        ({'date': arrow.get('20211101')}, {'date': '2021-11-01T00:00:00+00:00'}),
        (
            {'nested': {'uuid1': UUID(int=1), 'uuid2': UUID(int=2)}},
            {'nested': {'uuid1': str(UUID(int=1)), 'uuid2': str(UUID(int=2))}},
        ),
        (UUID, "<class 'uuid.UUID'>"),
        (arrow.get, '<function get(..)>'),
        (
            {'partial': partial(json.dumps, sort_keys=True)},
            {'partial': 'functools.partial(<function dumps(..)>, sort_keys=True)'},
        ),
        (MagicMock(), '<MagicMock id=(..)>'),
    ],
)
def test_make_diffable(value, expected):
    """Test recursive serialization in make_diffable."""
    result = make_diffable(value)

    assert result == expected
