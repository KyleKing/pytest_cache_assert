# pytest_cache_assert

Cache assertion data to simplify regression testing of complex serializable data

## Installation

`poetry add pytest_assert_check --dev`

## Quick Start

The primary use case of this package is regression testing of large dictionaries. You may have some parameterized test cases where you need to assert that a resulting dictionary is the same, but you don’t want to manually generate the expected fields and values and couple the test case to the source code. Instead you can cache or “record” the expected deserialized data structure, check the expected dictionary into version control, then regenerate on changes

This package can minimize test case logic, while improving test thoroughness

### Basic Example

Situation: You've created a new project with poetry called `package_a` with one file `source_file.py` and test `tests/test_file.py`

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

from pytest_cache_assert import check_assert


@pytest.mark.parametrize('name', ['Test Name 1', 'Test Name 2'])
def test_create_data(name):
    """Basic test of create_data()."""
    result = create_data(name=name)

    # One could manually create the expected dictionary
    cache = {'id': 9223372036854775807, 'signup_ts': None, 'friends': [], 'name': name}
    assert result == cache
    # Or use the pytest_cache_assert function to compare against the last recorded dictionary
    check_assert(result)  # FIXME: Update with changes to function signature
```

`pytest_cache_assert` will automatically create: `tests/cache-assert/source_file/test_file/test_create_data-000.json` (and `test_create_data-001.json`) for each of the parameters when first run by caching the result of `create_data(...)`. Below is the example for `test_create_data-000.json`. This file should be checked into version control and can be manually edited if needed or regenerated if the dictionary changes by deleting the file and re-running the tests

```json
{
    "_info": {
        "parameters":  ["Test Name 1"]
    },
    "_json": {
        "friends": [],
        "id": 9223372036854775807,
        "name": "Test Name 1",
        "signup_ts": None
    }
}
```

### More Examples

<!-- TODO: Create these more complex examples and cleanup general ideas -->

<!--
- match-accuracy: exact, subset, superset (enum)
- key_rules: Dict[str, Optional[Callable[[Any, Any], None]]
    - (String): rule_callable (ignore, check-likeness, custom)
        - Specify the key name or pattern of key names using dots for nesting and asterisks for wildcards (jmespath)
        - The rule callable can be any custom implementation or one of the recommended
            - The default assertion is an exact match, so any keys not specified here will be checked for exactness
            - The provided checks are for variable use cases
            - NoOp-ignore field
            - Check if null if value is null or check type-of (in-exact)
- transformer: custom serializer of Dict[str, Union[str, dict]]. Could use cattrs, marshmallow, Pydantic, or some custom function as long as the result is a dict
    - Can be used for additional checks with Cerberus or other library (custom_validator)
-->

You might have variable values with more complex logic to verify, such as dates, UUIDs, etc. These can be selectively ignored, matched-if-null, or some other user-specified check:

(Example with UUID and datetime)

- transformer = transformer or lambda res: res
- data = json.loads(…)[KEY_Data]
    - (Writes cache if first run)
- result = transformer()
- For each key_rule:
    - Call
    - Pop keys from both dictionaries if present
- For subset type, filter the dictionaries
- Normal pytest assert

The cached data can also be a super- or subset. You may only care that at minimum, certain fields exist and can allow some variability by setting …

(Example)

Or you may want to write your own custom checks against the deserialized data, such as with Cerberus or another library.

(Example)

### Even More Example

For more examples, see [Scripts](https://github.com/kyleking/pytest_cache_assert/scripts) or [Tests](https://github.com/kyleking/pytest_cache_assert/tests)

## Configuration Options

### Local

- `cache_name`: default is test name with -000 (or index of parameter)
    - Can be set to static string or custom formatter

### Global

- `custom directory` (set in pytest fixture like pytest-record)
    - Default is test directory/cache-assert/
- `record_rule`: regenerate on failure (re-raises assert, but updates cache). Default is to record once

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
