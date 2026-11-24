
from datetime import date

from flask import (
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for
)

from flask_login import login_required

from app.appointments import appointments_bp

from app.appointments.forms import (
    AvailabilityForm,
    AppointmentForm
)

from app.appointments.services import (
    get_availability,
    get_available_slots,
    register_appointment,
    AppointmentError
)

from app.models import Professional
from app.extensions import db


# =========================================
# HU-02 - Consulta de disponibilidad
# =========================================

@appointments_bp.route(
    "/availability",
    methods=["GET", "POST"]
)
@login_required
def availability():

    form = AvailabilityForm()

    professionals = Professional.query.filter_by(
        active=True
    ).order_by(
        Professional.name
    ).all()

    form.professional_id.choices = [
        (
            professional.id,
            f"{professional.name} - {professional.specialty}"
        )
        for professional in professionals
    ]

    slots = []
    selected_professional = None
    selected_date = None
    searched = False

    if form.validate_on_submit():

        selected_professional = db.session.get(
            Professional,
            form.professional_id.data
        )

        selected_date = form.selected_date.data

        slots = get_availability(
            form.professional_id.data,
            selected_date
        )

        searched = True

    available_count = sum(
        1 for slot in slots if slot["available"]
    )

    occupied_count = len(slots) - available_count

    return render_template(
        "availability.html",
        form=form,
        slots=slots,
        selected_professional=selected_professional,
        selected_date=selected_date,
        searched=searched,
        available_count=available_count,
        occupied_count=occupied_count
    )


# =========================================
# HU-03 - Consulta dinámica de horarios
# =========================================

@appointments_bp.route("/available-slots")
@login_required
def available_slots():

    professional_id = request.args.get(
        "professional_id",
        type=int
    )

    selected_date = request.args.get("date")

    if not professional_id or not selected_date:

        return jsonify({
            "slots": [],
            "error": "Seleccione un profesional y una fecha."
        }), 400

    try:

        appointment_date = date.fromisoformat(
            selected_date
        )

    except ValueError:

        return jsonify({
            "slots": [],
            "error": "La fecha seleccionada no es válida."
        }), 400

    if appointment_date < date.today():

        return jsonify({
            "slots": [],
            "error": "No se permiten fechas anteriores."
        }), 400

    slots = get_available_slots(
        professional_id,
        appointment_date
    )

    return jsonify({
        "slots": slots
    })


# =========================================
# HU-03 - Registro de citas
# =========================================

@appointments_bp.route(
    "/register",
    methods=["GET", "POST"]
)
@login_required
def register():

    form = AppointmentForm()

    professionals = Professional.query.filter_by(
        active=True
    ).order_by(
        Professional.name
    ).all()

    form.professional_id.choices = [
        (0, "Seleccione un profesional")
    ] + [
        (
            professional.id,
            f"{professional.name} - {professional.specialty}"
        )
        for professional in professionals
    ]

    if request.method == "GET":

        form.professional_id.data = request.args.get(
            "professional_id",
            default=0,
            type=int
        )

        requested_date = request.args.get("date")

        if requested_date:

            try:

                form.selected_date.data = date.fromisoformat(
                    requested_date
                )

            except ValueError:

                form.selected_date.data = date.today()

    slots = []

    if (
        form.professional_id.data
        and form.selected_date.data
        and form.selected_date.data >= date.today()
    ):

        slots = get_available_slots(
            form.professional_id.data,
            form.selected_date.data
        )

    form.start_time.choices = [
        ("", "Seleccione un horario")
    ] + [
        (slot, slot)
        for slot in slots
    ]

    if request.method == "GET":

        requested_time = request.args.get("start_time")

        if requested_time in slots:
            form.start_time.data = requested_time

    if form.validate_on_submit():

        try:

            appointment = register_appointment(
                patient_name=form.patient_name.data,
                professional_id=form.professional_id.data,
                appointment_date=form.selected_date.data,
                start_time=form.start_time.data
            )

            flash(
                f"Cita registrada correctamente. "
                f"Paciente: {appointment.patient_name}. "
                f"Fecha: {appointment.date.strftime('%d/%m/%Y')}. "
                f"Hora: {appointment.start_time.strftime('%H:%M')}.",
                "success"
            )

            return redirect(
                url_for("appointments.register")
            )

        except AppointmentError as error:

            flash(str(error), "danger")

    return render_template(
        "register_appointment.html",
        form=form,
        today=date.today().isoformat()
    )
