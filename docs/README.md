# pytest_cache_assert

Cache assertion data to simplify regression testing of complex serializable data

## Installation

`poetry add pytest_assert_check --dev`

## Usage

The primary use case of this package is regression testing of large, serializable dictionaries, such as from an API under development.

You may have parameterized test cases where you need to assert that the created dictionary stays the same, but you don’t want to manually generate the expected fields and values to compare. Instead you can capture a snapshot of the serialized data and cache the result then use the cached data to check for consistency in repeated test runs. The cached files should be checked into version control, which can be very useful as documentation

This package can minimize test case logic, while improving regression testing thoroughness

This project was heavily inspired by the excellent [pytest-recording](https://github.com/kiwicom/pytest-recording)

### Alternatives

- [pytest-recording](https://github.com/kiwicom/pytest-recording): this is the package I use and highly recommend for recording and replaying **external** API communication so that API requests only need to be made once for unit testing (i.e. recording API responses from Github's API called from a test suite)
- [pytest-snapshot](https://pypi.org/project/pytest-snapshot/): I only found this package after already releasing a 1.0.0 version of `pytest_assert_cache`. This package can be more configurable with a user-specified serializer and might be a good alternative. See their documentation for more info
- [snapshottest](https://github.com/syrusakbary/snapshottest): This was another find after releasing a 1.0.0 version and would probably be **a good alterantive for most users**
  - `pytest-snapshot` is much more configurable, has many more users, and is a better name
    - I really like the ability to quickly regenerate the cached files with [--snapshot-update](https://github.com/syrusakbary/snapshottest/blob/master/snapshottest/pytest.py)
    - [There is some interesting discussion on how best to handle fields that change between tests](https://github.com/syrusakbary/snapshottest/issues/21)
- [dirty-equals](https://github.com/samuelcolvin/dirty-equals): broadly check values (i.e. `assert result == {'counter': IsPositiveInt, ...}`, etc.) rather than accessing and checking each field individual, which makes test easier to write and output errors easier to review

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
def create_data(name: str) -> Dict:
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
  "_info": [
    {
      "func_args": {
        "name": "Test Name 1"
      },
      "test_file": "test_readme.py",
      "test_name": "test_create_data"
    }
  ],
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

```py
"""tests/test_readme_more.py."""

from contextlib import suppress
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from pytest_cache_assert import AssertRule, Wild, check_suppress, check_type


def test_assert_against_cache_key_rules(assert_against_cache):
    """Demonstrate use of `assert_rules`."""
    now = datetime.now()
    cached_data = {
        'date': str(now),
        'nested': {'uuid': str(uuid4())},
        'ignored': {'a': 1, 'b': 2},
    }
    test_data = {
        'date': str(now + timedelta(hours=3)),
        'nested': {'uuid': str(uuid4())},
        'ignored': {'recursively': {'a': {'b': {'c': 1}}}},
    }
    with suppress(AssertionError):
        # Ensures that the cache file has been created
        assert_against_cache(cached_data)

    assert_rules = [
        # To ignore values for 'ignored.a' and 'ignored.b', create a rule
        #   Here, we use the wildcard for dictionary keys
        AssertRule.build_re(pattern=['ignored', Wild.recur()], func=check_suppress),

        # Instead of suppressing, the type of data could be resolved and compared
        #   This is useful for datetime or UUID values where we expect variability
        AssertRule(pattern='date', func=check_type),
        AssertRule.build_re(pattern=['nested', 'uuid'], func=check_type),

        # Any "func" with arguments 'old' and 'new' can be used as a rule
    ]

    # Without assert rules, an AssertionError is raised
    with pytest.raises(AssertionError):
        assert_against_cache(test_data)
    # But, with the custom logic, the cache assertion check will succeed
    assert_against_cache(test_data, assert_rules=assert_rules)
```

### Even More Examples

For more example code, see the [scripts] directory or the [tests].

## Customization (`beta`)

> Note: this feature is to be considered `beta` and may change, however, I will do my best to keep the same interfaces

For 2.0.0, `pytest_cache_assert` was refactored to be more easily customizable with configuration options for not just the cache directory, but also for a way to override how files are named and to override how the cached test data is serialized and validated.

With these configuration options, users or 3rd party packages can replace the default package behavior, such as changing the file format for data serialization (`yaml`, `jsonlines`, etc.) and/or specifying a different serialization logic. All configuration options are available by creating a `cache_assert_config` fixture with the provided implementations.

- See `AssertConfig` in `plugin.py` for configuration options and more information
  - `always_write`: Always write to the cached file so that diffs can be examined in the user's VCS.
  - `cache_dir_rel_path`: String relative directory from `tests/`. Default resolves to `tests/assert-cache/`.
  - `cache_store`: Configurable class for managing the cache representation. Default is local JSON.
  - `converters`: register functions that handle conversion of unhandled types, such as pandas DataFrames
  - `validator`: Custom validator for identifying and summarizing the deviations from the cache.

```py
import pytest

from pytest_cache_assert.plugin import AssertConfig


@pytest.fixture(scope='module')
def cache_assert_config():
    return AssertConfig(cache_dir_rel_path='custom/cache/dir')
```

## Project Status

See the `Open Issues` and/or the [CODE_TAG_SUMMARY]. For release history, see the [CHANGELOG].

### Planned Global Configuration Options

These are ideas for future options that are not currently implemented, but could be if there is enough interest:

- PLANNED: [Provide CLI arguments like `pytest-recording`](https://github.com/kiwicom/pytest-recording/blob/484bb887dd43fcaf44149160d57b58a7215e2c8a/src/pytest_recording/plugin.py#L37-L70) (`request.config.getoption("--record-mode") or "none"`) for one-time changes to configuration
- PLANNED: Consider filters to prevent secrets from being cached: `filter_headers=[['authorization', 'id'], ['authorization', 'cookies']]` (Although, you should be using a pre-commit hook and formatting the dict before passing to to the cache)
- TODO: [Add tips from Jest on best practices](https://jestjs.io/docs/snapshot-testing#best-practices) -- treat snapshots as code, etc.

## Contributing

We welcome pull requests! For your pull request to be accepted smoothly, we suggest that you first open a GitHub issue to discuss your idea. For resources on getting started with the code base, see the below documentation:

- [DEVELOPER_GUIDE]
- [STYLE_GUIDE]
- [CONTRIBUTING]

## Code of Conduct

We follow the [Contributor Covenant Code of Conduct][contributor-covenant].

## Responsible Disclosure

If you have any security issue to report, please contact the project maintainers privately. You can reach us at [dev.act.kyle@gmail.com](mailto:dev.act.kyle@gmail.com).

## License

[LICENSE]

[changelog]: ./docs/CHANGELOG.md
[code_tag_summary]: ./docs/CODE_TAG_SUMMARY.md
[contributing]: ./docs/CONTRIBUTING.md
[contributor-covenant]: https://www.contributor-covenant.org
[developer_guide]: ./docs/DEVELOPER_GUIDE.md
[license]: https://github.com/kyleking/pytest_cache_assert/LICENSE
[scripts]: https://github.com/kyleking/pytest_cache_assert/scripts
[style_guide]: ./docs/STYLE_GUIDE.md
[tests]: https://github.com/kyleking/pytest_cache_assert/tests
