from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile("../instance/config.py")
    else:
        app.config.from_mapping(test_config)

    from .models import db

    db.init_app(app)
    CORS(app)

    from .token import jwt
    jwt.init_app(app)

    from .auth import authentication as auth
    app.register_blueprint(auth)

    return app
