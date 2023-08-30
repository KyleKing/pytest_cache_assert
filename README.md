# pytest_cache_assert

> **Warning**
>
> This project is deprecated in favor of [`syrupy`](https://github.com/tophat/syrupy), which has a larger user base and more features.
>
> To migrate:
>
> 1. Add the `syrupy` dependency and remove `pytest-cache-assert`
> 1. In your test, replace the fixture argument `assert_against_cache` with `snapshot`
>     1. Then replace `assert_against_cache(data)` with `assert data == snapshot`
> 1. Remove the `tests/assert-cache` directory
>
> See an example of a project that was migrated here: <https://github.com/KyleKing/tail-jsonl/commit/c3b32e20ad88407555b445ba796adda3cfe200d1>
>
> If you run into any issue migrating or have questions, feel free to open an issue on GitHub: <https://github.com/KyleKing/pytest_cache_assert/issues>.

Cache assertion data to simplify regression testing of complex serializable data

Documentation can be found on [Github (./docs)](./docs), [PyPi](https://pypi.org/project/pytest_cache_assert/), or [Hosted](https://pytest_cache_assert.kyleking.me/)!
