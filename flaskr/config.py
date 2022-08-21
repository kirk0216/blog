import os

import flaskr.db


class Config:
    SECRET_KEY = None

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevConfig(Config):
    SECRET_KEY = 'dev'
    TEMPLATES_AUTO_RELOAD = True
    ORIGIN = 'http://localhost:5000'
    DATABASE = flaskr.db.DevelopmentDatabase()
    DATABASE_URI = 'flaskr.sqlite'


class TestConfig(Config):
    SECRET_KEY = 'test'
    TESTING = True


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    TEMPLATES_AUTO_RELOAD = False
    SESSION_COOKIE_SECURE = True

    DATABASE = flaskr.db.ProductionDatabase()
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
