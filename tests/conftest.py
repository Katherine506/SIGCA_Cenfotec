
import pytest

from app import create_app
from app.extensions import db
from app.models import User
from config import TestConfig


@pytest.fixture
def app():

    application = create_app(TestConfig)

    with application.app_context():

        db.create_all()

        user = User(
            name="Usuario de prueba",
            email="test@example.com",
            role="administrador"
        )

        user.set_password("test-password")

        db.session.add(user)
        db.session.commit()

    yield application

    with application.app_context():

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
