
from datetime import date

from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, SubmitField
from wtforms.validators import DataRequired


class AvailabilityForm(FlaskForm):

    professional_id = SelectField(
        "Profesional",
        coerce=int,
        validators=[DataRequired()]
    )

    selected_date = DateField(
        "Fecha de atención",
        format="%Y-%m-%d",
        default=date.today,
        validators=[DataRequired()]
    )

    submit = SubmitField("Consultar disponibilidad")
