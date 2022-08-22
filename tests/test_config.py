import os

import flask

from flaskr.config import ProductionConfig, get_dev_db_uri, get_production_db_uri


def test_get_dev_db_uri(app):
    with app.app_context():
        expected = 'sqlite:///%s' % os.path.join(flask.current_app.instance_path, 'flaskr.sqlite')
        assert get_dev_db_uri() == expected


def test_get_production_db_uri():
    ProductionConfig.DB_HOST = 'localhost'
    ProductionConfig.DB_NAME = 'test'
    ProductionConfig.DB_USER = 'test_user'
    ProductionConfig.DB_PASS = 'password'

    expected = 'postgres+psycopg2://test_user:password@localhost/test'
    assert get_production_db_uri() == expected
