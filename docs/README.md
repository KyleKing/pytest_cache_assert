# pytest_cache_assert

Cache assertion data to simplify regression testing of complex serializable data

## Installation

`poetry add pytest_assert_check --dev`

## Quick Start

The primary use case of this package is regression testing of large dictionaries. You may have some parameterized test cases where you need to assert that a resulting dictionary is the same, but you don’t want to manually generate the expected fields and values and couple the test case to the source code. Instead you can cache or “record” the expected serialized data structure, check the expected dictionary into version control, then regenerate on changes

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

In your cached dictionary, you may have variable values with more complex logic to verify, such as dates, UUIDs, etc. These can be selectively ignored, matched-if-null, or some other user-specified check:

```py
from uuid import uuid4
from datetime import datetime

from pytest_cache_assert import check_assert

# TODO: Implement this example! Add as red test, then implement!

def test_variable_cache():
    """Demonstration of specifying custom assertion rules."""
    # TODO: support list indexing on top of jmespath...
    result = {"date": datetime.now(), {"nested": {"uuid": uuid4()}}}

    check_assert(result, ...)
```

The cached data can also be a super- or subset. You may only care that at minimum, certain fields exist and can allow some variability by setting `match_precision`

```py
# TODO: Maybe don't have match_precision as an option because recording means there won't ever be a sub/superset
# PLANNED: Also consider dropping the transformer for the validator. The package can only work with JSON-safe data when caching anyway
```

Or you may want to write your own custom checks against the serialized data, such as with Cerberus or another library.

```py
# TODO: Add example for custom cerberus checks with `validator()`
```

### Even More Example

For more examples, see [Scripts](https://github.com/kyleking/pytest_cache_assert/scripts) or [Tests](https://github.com/kyleking/pytest_cache_assert/tests)

## Global Configuration Options

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
