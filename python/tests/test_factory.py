from flaskr import create_app
from flaskr.config import TestConfig


def test_config():
    assert not create_app().testing
    assert create_app(TestConfig).testing
