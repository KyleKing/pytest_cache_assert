import pytest
from beartype import beartype
from flask import Flask


@beartype
def _create_app() -> Flask:
    """Minimal example from pytest-flask README.

    https://github.com/pytest-dev/pytest-flask/tree/a8d8ffaa90fe826e9642e13dba7d739e005f31a3#how-to-start

    """
    app = Flask(__name__)

    @app.route('/hello')
    def hello() -> str:
        """Hello endpoint."""
        return 'Hello, World!'

    return app  # noqa: RET504


@pytest.fixture()
@beartype
def app() -> Flask:
    return _create_app()


def test_pytest_flask_client(client, assert_against_cache):
    """Check that the pytest-flask fixture is serializable."""
    assert_against_cache({'client': client})
