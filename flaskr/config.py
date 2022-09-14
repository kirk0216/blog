import os
from urllib.parse import quote

import flask
import redis


class Config:
    SECRET_KEY = None

    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = False
    SESSION_REDIS = redis.from_url('redis://localhost:6379')

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

    # RESETPASSWORD_LINK_LIFETIME = 1 hour (60 seconds * 60 minutes)
    RESETPASSWORD_LINK_LIFETIME = 60 * 60


class DevConfig(Config):
    SECRET_KEY = 'dev'
    SERVER_NAME = 'localhost:5000'
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = False
    DATABASE_URI = 'sqlite:///%s'
    DATABASE_PATH = 'flaskr.sqlite'


def get_dev_db_uri():
    return DevConfig.DATABASE_URI % os.path.join(flask.current_app.instance_path, DevConfig.DATABASE_PATH)


class TestConfig(Config):
    SECRET_KEY = 'test'
    TESTING = True
    DATABASE_URI = 'sqlite:///%s'
    DATABASE_PATH = None
    WTF_CSRF_ENABLED = False


def get_test_db_uri():
    return TestConfig.DATABASE_URI % flask.current_app.config['DATABASE_PATH']


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    TEMPLATES_AUTO_RELOAD = False
    SESSION_COOKIE_SECURE = True
    SESSION_REDIS = redis.from_url('redis://redis:6379')

    DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s/%s'
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')


def get_production_db_uri():
    return ProductionConfig.DATABASE_URI % (
        quote(ProductionConfig.DB_USER), quote(ProductionConfig.DB_PASS), quote(ProductionConfig.DB_HOST), quote(ProductionConfig.DB_NAME)
    )
