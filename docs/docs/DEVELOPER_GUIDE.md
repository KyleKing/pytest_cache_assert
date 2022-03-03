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

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/). Replace `...` with the API token generated on TestPyPi|PyPi respectively

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
| `pytest_cache_assert/__init__.py`                    |            4 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/__init__.py`      |            0 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/caching.py`       |           31 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/config.py`        |            6 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/constants.py`     |           22 |         1 |          0 | 95.5%      |
| `pytest_cache_assert/_check_assert/differ.py`        |          108 |        10 |          0 | 90.7%      |
| `pytest_cache_assert/_check_assert/error_message.py` |           10 |         0 |          0 | 100.0%     |
| `pytest_cache_assert/_check_assert/key_rules.py`     |           61 |         3 |          0 | 95.1%      |
| `pytest_cache_assert/_check_assert/serializer.py`    |           44 |         3 |          0 | 93.2%      |
| `pytest_cache_assert/main.py`                        |           41 |         7 |          0 | 82.9%      |
| `pytest_cache_assert/plugin.py`                      |           44 |         2 |          0 | 95.5%      |
| **Totals**                                           |          371 |        26 |          0 | 93.0%      |

Generated on: 2022-03-02T22:05:20.207813
<!-- {cte} -->
