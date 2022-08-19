import os


class Config:
    SECRET_KEY = None
    DATABASE = 'flaskr.sqlite'

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevConfig(Config):
    SECRET_KEY = 'dev'
    TEMPLATES_AUTO_RELOAD = True
    ORIGIN = 'http://localhost:5000'


class TestConfig(Config):
    SECRET_KEY = 'test'
    TESTING = True


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    TEMPLATES_AUTO_RELOAD = False
    SESSION_COOKIE_SECURE = True
