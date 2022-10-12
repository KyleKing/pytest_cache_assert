import pytest
from flask import Flask


def _create_app():
    """Minimal example from pytest-flask README.

    https://github.com/pytest-dev/pytest-flask/tree/a8d8ffaa90fe826e9642e13dba7d739e005f31a3#how-to-start

    """
    app = Flask(__name__)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app


@pytest.fixture
def app():
    return _create_app()


def test_pytest_flask_client(client, assert_against_cache):
    """Check that the pytest-flask fixture is serializable."""
    assert_against_cache({'client': client})
