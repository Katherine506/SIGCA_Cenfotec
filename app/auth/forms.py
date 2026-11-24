
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length
)


class LoginForm(FlaskForm):

    email = StringField(
        "Correo electrónico",
        validators=[
            DataRequired(
                message="El correo es obligatorio."
            ),
            Email(
                message="Ingrese un correo válido."
            ),
            Length(max=120)
        ]
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(
                message="La contraseña es obligatoria."
            )
        ]
    )

    submit = SubmitField("Iniciar sesión")
