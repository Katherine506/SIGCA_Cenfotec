
from flask import Flask, render_template
from flask_login import login_required

from config import Config
from app.extensions import db, login_manager, csrf
from app.models import User
from app.auth import auth_bp


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(auth_bp)

    @app.route("/")
    @login_required
    def index():
        return render_template("dashboard.html")

    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "application": "SIGCA"
        }

    with app.app_context():
        db.create_all()

    return app
