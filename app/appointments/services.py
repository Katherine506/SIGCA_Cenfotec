
from datetime import date, datetime, time, timedelta

from sqlalchemy.exc import IntegrityError

from app.models import Professional, Schedule, Appointment
from app.extensions import db


SLOT_DURATION_MINUTES = 30


class AppointmentError(Exception):
    """Error relacionado con las reglas de negocio de citas."""
    pass


# =========================================
# HU-02 - Consulta de disponibilidad
# =========================================

def get_availability(professional_id, selected_date):

    professional = db.session.get(
        Professional,
        professional_id
    )

    if professional is None or not professional.active:
        return []

    schedules = Schedule.query.filter_by(
        professional_id=professional_id,
        weekday=selected_date.weekday()
    ).order_by(
        Schedule.start_time
    ).all()

    appointments = Appointment.query.filter_by(
        professional_id=professional_id,
        date=selected_date,
        status="activa"
    ).all()

    duration = timedelta(minutes=SLOT_DURATION_MINUTES)

    occupied_periods = [
        (
            datetime.combine(
                selected_date,
                appointment.start_time
            ),
            datetime.combine(
                selected_date,
                appointment.start_time
            ) + duration
        )
        for appointment in appointments
    ]

    slots = {}

    for schedule in schedules:

        current = datetime.combine(
            selected_date,
            schedule.start_time
        )

        end = datetime.combine(
            selected_date,
            schedule.end_time
        )

        while current + duration <= end:

            slot_end = current + duration

            occupied = any(
                current < occupied_end
                and slot_end > occupied_start
                for occupied_start, occupied_end
                in occupied_periods
            )

            slots[current.time()] = {
                "time": current.strftime("%H:%M"),
                "available": not occupied
            }

            current += duration

    return [
        slots[slot_time]
        for slot_time in sorted(slots)
    ]


def get_available_slots(professional_id, selected_date):

    return [
        slot["time"]
        for slot in get_availability(
            professional_id,
            selected_date
        )
        if slot["available"]
    ]


# =========================================
# HU-03 - Registro de citas
# =========================================

def register_appointment(
    patient_name,
    professional_id,
    appointment_date,
    start_time
):

    patient_name = (patient_name or "").strip()

    if not patient_name:
        raise AppointmentError(
            "El nombre del paciente es obligatorio."
        )

    if len(patient_name) > 120:
        raise AppointmentError(
            "El nombre del paciente no puede superar "
            "120 caracteres."
        )

    if (
        not isinstance(appointment_date, date)
        or isinstance(appointment_date, datetime)
    ):
        raise AppointmentError(
            "La fecha de la cita no es válida."
        )

    if appointment_date < date.today():
        raise AppointmentError(
            "No se pueden registrar citas en fechas anteriores."
        )

    professional = db.session.get(
        Professional,
        professional_id
    )

    if professional is None or not professional.active:
        raise AppointmentError(
            "El profesional seleccionado no está disponible."
        )

    try:

        appointment_time = time.fromisoformat(start_time)

    except (ValueError, TypeError):

        raise AppointmentError(
            "El horario seleccionado no es válido."
        )

    if (
        appointment_time.second
        or appointment_time.microsecond
        or appointment_time.tzinfo is not None
    ):
        raise AppointmentError(
            "El horario seleccionado no es válido."
        )

    available_slots = get_available_slots(
        professional_id,
        appointment_date
    )

    if appointment_time.strftime("%H:%M") not in available_slots:
        raise AppointmentError(
            "El horario seleccionado no está disponible."
        )

    appointment = Appointment(
        patient_name=patient_name,
        professional_id=professional_id,
        date=appointment_date,
        start_time=appointment_time,
        status="activa"
    )

    try:

        db.session.add(appointment)
        db.session.commit()

    except IntegrityError as error:

        db.session.rollback()

        raise AppointmentError(
            "No fue posible registrar la cita. "
            "El horario podría estar ocupado."
        ) from error

    return appointment
