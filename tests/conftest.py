"""PyTest configuration.

Note: the calcipy imports are required for a nicer test HTML report

"""

from pathlib import Path

import boto3
import pytest
from beartype import beartype
from beartype.typing import Dict, Union
from calcipy.dev.conftest import pytest_configure  # noqa: F401
from calcipy.dev.conftest import pytest_html_results_table_header  # noqa: F401
from calcipy.dev.conftest import pytest_html_results_table_row  # noqa: F401
from calcipy.dev.conftest import pytest_runtest_makereport  # noqa: F401
from moto import mock_s3

from pytest_cache_assert import AssertConfig, CacheAssertContainerKeys, Converter, register
from pytest_cache_assert._check_assert.constants import DEF_CACHE_DIR_NAME

from .configuration import TEST_TMP_CACHE, clear_test_cache


@pytest.fixture()
@beartype
def fix_cache_path() -> Path:
    """Fixture to clear and return the test cache directory for use.

    Returns:
        Path: Path to the test cache directory

    """
    clear_test_cache()
    return TEST_TMP_CACHE


@pytest.fixture()
@beartype
def fix_tmp_assert(fix_cache_path: Path) -> Dict[str, Union[str, Path]]:
    """Fixture to temporary assert directory and keyword arguments.

    Args:
        fix_cache_path: pytest fixture for temporary directory

    Returns:
        Path: Path to the test cache directory

    """
    return {
        'path_cache_dir': fix_cache_path,
        'cache_name': 'test_assert_against_cache.json',
    }


# https://github.com/beartype/bearboto3/blob/c212ca885623dd3b0c45868ec2ed66e8c5b8043c/tests/s3/s3_fixtures.py#L7-L10
@pytest.fixture()
def gen_s3_client():
    with mock_s3():
        yield boto3.client('s3')


class CustomType:
    """Arbitrary custom type used for testing user configuration.

    Note: I previously tested the `to_json(origin='records')` version of the pandas dataframe serializer to override the default, but this test suite was sometimes restoring the default and sometimes not, which was hard to troubleshoot

    """

    @staticmethod
    def to_str(_arg) -> str:
        return 'Serialized!'


@pytest.fixture(autouse=True)  # FYI: This is a workaround since other internal tests register a different config
@beartype
def register_custom_cache_assert_config() -> None:
    """Register a new AssertConfig."""
    assert_config = AssertConfig(
        always_write=False,
        cache_dir_rel_path=f'{DEF_CACHE_DIR_NAME}-custom',
        converters=[
            Converter(types=[CustomType], func=CustomType.to_str),
        ],
    )
    register(CacheAssertContainerKeys.CONFIG, assert_config)
