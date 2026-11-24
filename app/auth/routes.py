
from flask import (
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.models import User



@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():

        email = form.email.data.strip().lower()

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(
            form.password.data
        ):

            login_user(user)

            flash(
                "Sesión iniciada correctamente.",
                "success"
            )

            return redirect(url_for("index"))

        flash(
            "Correo electrónico o contraseña incorrectos.",
            "danger"
        )

    return render_template(
        "login.html",
        form=form
    )


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash(
        "Sesión cerrada correctamente.",
        "success"
    )

    return redirect(url_for("auth.login"))
