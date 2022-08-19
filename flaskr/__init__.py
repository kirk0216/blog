import os

from flask import Flask
from flaskr.config import DevConfig


def create_app(app_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if app_config is None:
        app.config.from_object(DevConfig)
    else:
        app.config.from_object(app_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from . import comment
    app.register_blueprint(comment.bp)

    from . import profile
    app.register_blueprint(profile.bp)

    return app
