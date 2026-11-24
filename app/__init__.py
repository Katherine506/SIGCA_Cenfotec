
from flask import Flask

from config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @app.route("/")
    def index():
        return "Bienvenido a SIGCA - Centro Integral Horizonte"

    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "application": "SIGCA"
        }

    return app
