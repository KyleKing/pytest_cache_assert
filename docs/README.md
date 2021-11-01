# pytest_cache_assert

Cache assertion data to simplify regression testing of complex serializable data

## Installation

`poetry add pytest_assert_check --dev`

## Quick Start

The primary use case of this package is regression testing of large dictionaries. You may have some parameterized test cases where you need to assert that a resulting dictionary is the same, but you don’t want to manually generate the expected fields and values and couple the test case to the source code. Instead you can cache or “record” the expected serialized data structure, check the expected dictionary into version control, then regenerate on changes

This package can minimize test case logic, while improving test thoroughness

This project was heavily inspired by the excellent [pytest-recording](https://github.com/kiwicom/pytest-recording)

### Basic Example

You've created a new project called `package_a` with one file `package_a/source_file.py` and test `tests/test_file.py`

```py
"""package_a/source_file.py"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from beartype import beartype
from pydantic import BaseModel


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
```

```py
"""tests/test_file.py"""

import pytest

from package_a.source_file import create_data


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
```

`pytest_cache_assert` will automatically create: `tests/cache-assert/source_file/test_file/test_create_data-[Test Name 1].json` (and `test_create_data[Test Name 2].json`) for each of the parameters when first run by caching the `result`. Below is the example for `test_create_data-[Test Name 1].json`

```json
{
  "_info": {
    "func_args": {
      "name": "Test Name 1"
    },
    "test_file": ".../tests/test_file.py",
    "test_name": "test_create_data"
  },
  "_json": {
    "friends": [],
    "id": 9223372036854775807,
    "name": "Test Name 1",
    "signup_ts": null
  }
}
```

The cached JSON files must be checked into version control and if needed, can be manually edited or deleted so that they will be regenerated when the test suite is next run

### More Examples

In your cached dictionary, you may have variable values with more complex logic to verify, such as dates, UUIDs, etc. These can be selectively ignored, matched-if-null, or some other user-specified check:

<!-- TODO: Support Nested KeyRules -->
<!-- TODO: Use a class instead of an asterisk -->
<!-- TODO: Support filtering all keys below ... (i.e. two asterisk) -->
<!-- TODO: Sort by key names in reverse (most specific first) -->

```py
"""tests/test_main.py."""

from uuid import uuid4
from datetime import datetime, timedelta

from pytest_cache_assert import KeyRule, check_suppress, check_type, Wildcards


def test_assert_against_cache_key_rules(assert_against_cache):
    """Demonstrate use of `key_rules`."""
    # NOTE: all data passed to assert_against_cache must be JSON Serializable (i.e. from Marshmallow or Pydantic, etc.)
    now = datetime.now()
    cached_data = {'date': str(now), {'nested': {'uuid': str(uuid4())}}, {'ignored': {'a': 1, 'b': 2}}}
    test_data = {'date': str(now + timedelta(hours=3)), {'nested': {'uuid': str(uuid4())}}}
    #
    key_rules = [
      # Suppress keys 'ignored.a' and 'ignored.b' with the SINGLE wildcard
      # If there were a 'ignored.c.something', the Wildcard.RECURSIVE could be used
      KeyRule(pattern=['ignored', Wildcards.SINGLE], func=check_suppress),
      # Ensure that values are of the same type. This is useful if you expect datetime objects and want to raise
      #   if one value is Null (or you have a number stored as a string or UUID, etc.)
      KeyRule(pattern=['date'], func=check_type),
      KeyRule(pattern=['nested', 'uuid'], func=check_type),
      # The KeyRule function can be replaced with any function that accepts keyword arguments 'old' and 'new'
    ]
    #
    # Run twice to ensure that the initial cache file exists and that the key_rules suppress any errors
    assert_against_cache(cached_data, key_rules=key_rules)
    assert_against_cache(test_data, key_rules=key_rules)

    # Verify that without key rules, an AssertionError is raised
    with pytest.raises(AssertionError, match=DEF_ERROR_MESSAGE):
        assert_against_cache(test_data)  # act
```

Or you may want to write your own custom checks against the serialized data, such as with Cerberus or another library. This is possible with the `validator` callable. The default validator is a no-op and that may be replaced with any custom function that raises an Exception on error.

```py
"""tests/test_main.py."""

import re

import pytest
from beartype import beartype
from cerberus import Validator
from cerberus.schema import SchemaError


@beartype
def cerberus_validator(test_data: TEST_DATA_TYPE) -> None:
    """Cerberus custom validator example."""
    validator = Validator({'result': {'type': 'int'}})
    assert validator.validate(test_data)


def test_assert_against_cache_validator(assert_against_cache):
    """Test the validator."""
    expected = re.escape("{'result': [{'type': ['Unsupported types: int']}]}")

    with pytest.raises(SchemaError, match=expected):
        assert_against_cache({'result': False}, validator=cerberus_validator)  # act
```

### Even More Example

For more examples, see [Scripts](https://github.com/kyleking/pytest_cache_assert/scripts) or [Tests](https://github.com/kyleking/pytest_cache_assert/tests)

<!--
## Global Configuration Options

- `custom directory` (set in pytest fixture like pytest-record)
    - Default is test directory/cache-assert/
- `record_rule`: regenerate on failure (re-raises assert, but updates cache). Default is to record once

```py
import pytest


# TODO: Not currently used...
@pytest.fixture(scope='module')
def cache_assert_config():
    return {
        'rel_path_cache_dir': '..........',
        'record_mode': 'rewrite',  # TODO: Consider record mode
        'filter_headers': ['authorization'],  # TODO: Consider filters to prevent secrets from being stored
    }
```
 -->

## Roadmap

See the `Open Issues` and `Milestones` for current status and [./docs/CODE_TAG_SUMMARY.md](./docs/CODE_TAG_SUMMARY.md) for annotations in the source code.

For release history, see the [./docs/CHANGELOG.md](./docs/CHANGELOG.md)

## Contributing

See the Developer Guide, Contribution Guidelines, etc

- [./docs/DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md)
- [./docs/STYLE_GUIDE.md](./docs/STYLE_GUIDE.md)
- [./docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md)
- [./docs/CODE_OF_CONDUCT.md](./docs/CODE_OF_CONDUCT.md)
- [./docs/SECURITY.md](./docs/SECURITY.md)

## License

[LICENSE](https://github.com/kyleking/pytest_cache_assert/LICENSE)
