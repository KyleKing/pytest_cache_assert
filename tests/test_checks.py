"""Test plugin.py."""

import re
from _pytest.assertion import pytest_assertrepr_compare
import pytest
from beartype import beartype
from cerberus import Validator
from cerberus.schema import SchemaError

from pytest_cache_assert._check_assert.constants import TEST_DATA_TYPE
from pytest_cache_assert.checks import assert_against_cache


def test_assert_against_cache_failure(fix_tmp_assert):
    """Test that a difference in test_data and cached data generates an error."""
    assert_against_cache({'result': False}, **fix_tmp_assert)

    with pytest.raises(AssertionError, match=''):
        assert_against_cache({'result': True}, **fix_tmp_assert)  # act


@beartype
def cerberus_validator(test_data: TEST_DATA_TYPE) -> None:
    """Cerberus custom validator example."""
    validator = Validator({'result': {'type': 'int'}})
    assert validator.validate(test_data)


def test_assert_against_cache_validator(fix_tmp_assert):
    """Test the validator."""
    expected = re.escape("{'result': [{'type': ['Unsupported types: int']}]}")

    with pytest.raises(SchemaError, match=expected):
        assert_against_cache({'result': False}, validator=cerberus_validator, **fix_tmp_assert)  # act
