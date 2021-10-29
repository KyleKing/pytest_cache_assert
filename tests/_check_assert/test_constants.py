"""Test constants.py."""

from pytest_cache_assert._check_assert.constants import KEY_NAME_DATA, KEY_NAME_META


def test_sort_key_names():
    """Test that the constant keys are sorted with metadata always first."""
    expected_order = [KEY_NAME_META, KEY_NAME_DATA]

    result = sorted(expected_order[::-1])  # noqa: C415

    assert result == expected_order
