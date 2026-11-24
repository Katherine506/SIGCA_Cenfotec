
from app.models import User


def test_login_page(client):

    response = client.get("/auth/login")

    assert response.status_code == 200
    assert b"Iniciar" in response.data


def test_valid_credentials(client):

    response = client.post(
        "/auth/login",
        data={
            "email": "test@example.com",
            "password": "test-password"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Bienvenido" in response.data
    assert b"Usuario de prueba" in response.data


def test_invalid_password(client):

    response = client.post(
        "/auth/login",
        data={
            "email": "test@example.com",
            "password": "incorrect-password"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"incorrectos" in response.data

    protected = client.get("/")
    assert protected.status_code == 302


def test_nonexistent_user(client):

    response = client.post(
        "/auth/login",
        data={
            "email": "unknown@example.com",
            "password": "test-password"
        },
        follow_redirects=True
    )

    assert b"incorrectos" in response.data

    protected = client.get("/")
    assert protected.status_code == 302


def test_empty_credentials(client):

    response = client.post(
        "/auth/login",
        data={
            "email": "",
            "password": ""
        }
    )

    assert response.status_code == 200
    assert b"obligatorio" in response.data

    protected = client.get("/")
    assert protected.status_code == 302


def test_protected_route(client):

    response = client.get("/")

    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_logout(client):

    client.post(
        "/auth/login",
        data={
            "email": "test@example.com",
            "password": "test-password"
        }
    )

    assert client.get("/").status_code == 200

    response = client.post(
        "/auth/logout",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Iniciar" in response.data

    protected = client.get("/")

    assert protected.status_code == 302
    assert "/auth/login" in protected.location


def test_password_is_hashed(app):

    with app.app_context():

        user = User.query.filter_by(
            email="test@example.com"
        ).first()

        assert user is not None
        assert user.password_hash != "test-password"
        assert user.check_password("test-password")
        assert not user.check_password("incorrect-password")
