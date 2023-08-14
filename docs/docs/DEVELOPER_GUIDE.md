# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/pytest_cache_assert.git
cd pytest_cache_assert
poetry install --sync

# See the available tasks
poetry run calcipy
# Or use a local 'run' file (so that 'calcipy' can be extended)
./run

# Run the default task list (lint, auto-format, test coverage, etc.)
./run main

# Make code changes and run specific tasks as needed:
./run lint.fix test
```

## Publishing

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/). Replace `...` with the API token generated on TestPyPi or PyPi respectively

```sh
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi ...

./run main pack.publish --to-test-pypi
# If you didn't configure a token, you will need to provide your username and password to publish
```

To publish to the real PyPi

```sh
poetry config pypi-token.pypi ...
./run release

# Or for a pre-release
./run release --suffix=rc
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                                 |   Statements |   Missing |   Excluded | Coverage   |
|------------------------------------------------------|--------------|-----------|------------|------------|
| `pytest_cache_assert/__init__.py`                    |           24 |         0 |         17 | 100.0%     |
| `pytest_cache_assert/_check_assert/__init__.py`      |            0 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/assert_config.py` |           23 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/assert_rules.py`  |           87 |         8 |          0 | 89.3%      |
| `pytest_cache_assert/_check_assert/cache_store.py`   |           45 |         4 |          0 | 94.9%      |
| `pytest_cache_assert/_check_assert/caching.py`       |           39 |         0 |          0 | 98.3%      |
| `pytest_cache_assert/_check_assert/config.py`        |           28 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/constants.py`     |           17 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/converter.py`     |            6 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/differ.py`        |           41 |         2 |          0 | 95.2%      |
| `pytest_cache_assert/_check_assert/error_message.py` |           24 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/serializer.py`    |          122 |         8 |          0 | 95.5%      |
| `pytest_cache_assert/_check_assert/validator.py`     |           20 |         1 |          0 | 96.9%      |
| `pytest_cache_assert/main.py`                        |           33 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/plugin.py`                      |           56 |         5 |          0 | 90.5%      |
| **Totals**                                           |          565 |        28 |         17 | 95.1%      |

Generated on: 2023-08-14
<!-- {cte} -->
