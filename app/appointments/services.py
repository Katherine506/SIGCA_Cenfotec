
from datetime import datetime, timedelta

from app.models import Professional, Schedule, Appointment
from app.extensions import db


SLOT_DURATION_MINUTES = 30


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
            datetime.combine(selected_date, appointment.start_time),
            datetime.combine(selected_date, appointment.start_time)
            + duration
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
                for occupied_start, occupied_end in occupied_periods
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
