
from getpass import getpass

from app import create_app
from app.extensions import db
from app.models import User


app = create_app()


def create_admin():

    with app.app_context():

        print("Creación de administrador SIGCA")

        name = input("Nombre: ").strip()
        email = input("Correo electrónico: ").strip().lower()

        if not name or not email:
            print("El nombre y el correo son obligatorios.")
            return

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            print("El usuario ya existe.")
            return

        password = getpass("Contraseña: ")
        confirmation = getpass("Confirmar contraseña: ")

        if len(password) < 12:
            print("La contraseña debe tener al menos 12 caracteres.")
            return

        if password != confirmation:
            print("Las contraseñas no coinciden.")
            return

        user = User(
            name=name,
            email=email,
            role="administrador"
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print("Administrador creado correctamente.")


if __name__ == "__main__":
    create_admin()
