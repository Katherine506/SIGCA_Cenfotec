from datetime import date

from flask_wtf import FlaskForm

from wtforms import (
    SelectField,
    DateField,
    SubmitField,
    StringField
)

from wtforms.validators import DataRequired, Length


# =========================================
# HU-02 - Consulta de disponibilidad
# =========================================

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

    submit = SubmitField(
        "Consultar disponibilidad"
    )


# =========================================
# HU-03 - Registro de citas
# =========================================

class AppointmentForm(FlaskForm):

    patient_name = StringField(
        "Nombre completo del paciente",
        validators=[
            DataRequired(
                message="Ingrese el nombre del paciente."
            ),
            Length(
                max=120,
                message="El nombre no puede superar 120 caracteres."
            )
        ]
    )

    professional_id = SelectField(
        "Profesional",
        coerce=int,
        validators=[
            DataRequired(
                message="Seleccione un profesional."
            )
        ]
    )

    selected_date = DateField(
        "Fecha de atención",
        format="%Y-%m-%d",
        default=date.today,
        validators=[
            DataRequired(
                message="Seleccione una fecha válida."
            )
        ]
    )

    start_time = SelectField(
        "Horario disponible",
        choices=[],
        validators=[
            DataRequired(
                message="Seleccione un horario disponible."
            )
        ]
    )

    submit = SubmitField("Registrar cita")


# =========================================
# HU-04 - Gestión de citas
# =========================================

class AppointmentSearchForm(FlaskForm):

    search = StringField(
        "Buscar paciente",
        validators=[
            Length(max=120)
        ]
    )

    status = SelectField(
        "Estado",
        choices=[
            ("", "Todos los estados"),
            ("activa", "Activas"),
            ("cancelada", "Canceladas")
        ]
    )

    submit = SubmitField("Buscar")


class RescheduleAppointmentForm(FlaskForm):

    selected_date = DateField(
        "Nueva fecha de atención",
        format="%Y-%m-%d",
        validators=[
            DataRequired(
                message="Seleccione una fecha válida."
            )
        ]
    )

    start_time = SelectField(
        "Nuevo horario",
        choices=[],
        validators=[
            DataRequired(
                message="Seleccione un horario disponible."
            )
        ]
    )

    submit = SubmitField(
        "Confirmar reprogramación"
    )


class CancelAppointmentForm(FlaskForm):

    submit = SubmitField(
        "Confirmar cancelación"
    )