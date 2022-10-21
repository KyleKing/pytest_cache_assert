# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/pytest_cache_assert.git
cd pytest_cache_assert
poetry install

# See the available tasks
poetry run doit list

# Run the default task list (lint, auto-format, test coverage, etc.)
poetry run doit --continue

# Make code changes and run specific tasks as needed:
poetry run doit run test
```

## Publishing

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/). Replace `...` with the API token generated on TestPyPi or PyPi respectively

```sh
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi ...

poetry run doit run publish_test_pypi
# If you didn't configure a token, you will need to provide your username and password to publish
```

To publish to the real PyPi

```sh
poetry config pypi-token.pypi ...
poetry run doit run publish

# For a full release, triple check the default tasks, increment the version, rebuild documentation (twice), and publish!
poetry run doit run --continue
poetry run doit run cl_bump lock document deploy_docs publish

# For pre-releases use cl_bump_pre
poetry run doit run cl_bump_pre -p rc
poetry run doit run lock document deploy_docs publish
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                                 |   Statements |   Missing |   Excluded | Coverage   |
|------------------------------------------------------|--------------|-----------|------------|------------|
| `pytest_cache_assert/__init__.py`                    |            9 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/__init__.py`      |            0 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/assert_config.py` |           24 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/assert_rules.py`  |           87 |         8 |          0 | 90.8%      |
| `pytest_cache_assert/_check_assert/cache_store.py`   |           44 |         6 |          0 | 86.4%      |
| `pytest_cache_assert/_check_assert/caching.py`       |           36 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/config.py`        |           27 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/constants.py`     |           17 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/converter.py`     |            6 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/differ.py`        |           41 |         2 |          0 | 95.1%      |
| `pytest_cache_assert/_check_assert/error_message.py` |           20 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/serializer.py`    |          121 |         7 |          0 | 94.2%      |
| `pytest_cache_assert/_check_assert/validator.py`     |           23 |         3 |          0 | 87.0%      |
| `pytest_cache_assert/main.py`                        |           27 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/plugin.py`                      |           45 |         2 |          0 | 95.6%      |
| **Totals**                                           |          527 |        28 |          0 | 94.7%      |

Generated on: 2022-10-20
<!-- {cte} -->
