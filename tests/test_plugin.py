"""Test plugin.py."""

import json
from functools import partial
from uuid import UUID

import pendulum
import pytest

from pytest_cache_assert.plugin import _serialize


def test_assert_against_cache_failure(fix_test_cache, assert_against_cache):
    """Test that a difference in test_data and cached data generates an error."""
    kwargs = {
        'path_cache_dir': fix_test_cache / 'custom/nested/dir',
        'cache_name': 'test_assert_against_cache_failure-00.json',
    }

    assert_against_cache({'result': False}, **kwargs)  # act

    with pytest.raises(AssertionError):
        assert_against_cache({'result': True}, **kwargs)


# FIXME: Convert to hypothesis
@pytest.mark.parametrize(
    ('value', 'expected'), [
        ('20211101', '20211101'),
        (pendulum.parse('20211101'), '2021-11-01T00:00:00+00:00'),
        ({'date': pendulum.parse('20211101')}, {'date': '2021-11-01T00:00:00+00:00'}),
        (
            {'nested': {'uuid1': UUID(int=1), 'uuid2': UUID(int=2)}},
            {'nested': {'uuid1': str(UUID(int=1)), 'uuid2': str(UUID(int=2))}},
        ),
        (UUID, "<class 'uuid.UUID'>"),
        (pendulum.parse, '<function parse(..)>'),
        (
            {'partial': partial(json.dumps, sort_keys=True)},
            {'partial': 'functools.partial(<function dumps(..)>, sort_keys=True)'},
        ),
    ],
)
def test_serialize(value, expected):
    """Test serialization."""
    result = _serialize(value)

    assert result == expected
