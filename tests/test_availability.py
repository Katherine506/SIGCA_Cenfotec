
from datetime import date, time

import pytest

from app.extensions import db
from app.models import (
    User,
    Professional,
    Schedule,
    Appointment
)

from app.appointments.services import (
    get_availability,
    get_available_slots
)


TEST_DATE = date(2026, 11, 24)


@pytest.fixture
def professional_id(app):

    with app.app_context():

        professional = Professional(
            name="Profesional de prueba",
            specialty="Medicina general",
            active=True
        )

        db.session.add(professional)
        db.session.flush()

        schedules = [
            Schedule(
                professional_id=professional.id,
                weekday=1,
                start_time=time(8, 0),
                end_time=time(12, 0)
            ),
            Schedule(
                professional_id=professional.id,
                weekday=1,
                start_time=time(13, 0),
                end_time=time(17, 0)
            )
        ]

        db.session.add_all(schedules)
        db.session.commit()

        return professional.id


@pytest.fixture
def authenticated_client(app, client):

    with app.app_context():

        user = User(
            name="Usuario de prueba",
            email="availability@example.com",
            role="administrador"
        )

        user.set_password("TestPassword123!")

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/auth/login",
        data={
            "email": "availability@example.com",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 302

    return client


def add_appointment(
    professional_id,
    appointment_date=TEST_DATE,
    start_time=time(9, 0),
    status="activa"
):

    appointment = Appointment(
        professional_id=professional_id,
        patient_name="Paciente ficticio",
        date=appointment_date,
        start_time=start_time,
        status=status
    )

    db.session.add(appointment)
    db.session.commit()

    return appointment


# CP-HU02-01
def test_available_working_day(app, professional_id):

    with app.app_context():

        slots = get_available_slots(
            professional_id,
            TEST_DATE
        )

        assert len(slots) == 16
        assert "08:00" in slots
        assert "16:30" in slots


# CP-HU02-02
def test_day_without_schedule(app, professional_id):

    with app.app_context():

        slots = get_available_slots(
            professional_id,
            date(2026, 11, 28)
        )

        assert slots == []


# CP-HU02-03
def test_nonexistent_professional(app):

    with app.app_context():

        assert get_available_slots(
            999999,
            TEST_DATE
        ) == []


# CP-HU02-04
def test_inactive_professional(app, professional_id):

    with app.app_context():

        professional = db.session.get(
            Professional,
            professional_id
        )

        professional.active = False
        db.session.commit()

        assert get_available_slots(
            professional_id,
            TEST_DATE
        ) == []


# CP-HU02-05
def test_active_appointment_blocks_slot(
    app,
    professional_id
):

    with app.app_context():

        add_appointment(professional_id)

        slots = get_available_slots(
            professional_id,
            TEST_DATE
        )

        assert "09:00" not in slots
        assert len(slots) == 15

        all_slots = get_availability(
            professional_id,
            TEST_DATE
        )

        occupied = [
            slot for slot in all_slots
            if slot["time"] == "09:00"
        ]

        assert occupied == [
            {
                "time": "09:00",
                "available": False
            }
        ]


# CP-HU02-06
def test_cancelled_appointment_releases_slot(
    app,
    professional_id
):

    with app.app_context():

        add_appointment(
            professional_id,
            status="cancelada"
        )

        slots = get_available_slots(
            professional_id,
            TEST_DATE
        )

        assert "09:00" in slots
        assert len(slots) == 16


# CP-HU02-07
def test_other_professional_appointment(
    app,
    professional_id
):

    with app.app_context():

        other = Professional(
            name="Otro profesional",
            specialty="Nutrición",
            active=True
        )

        db.session.add(other)
        db.session.commit()

        add_appointment(other.id)

        slots = get_available_slots(
            professional_id,
            TEST_DATE
        )

        assert "09:00" in slots
        assert len(slots) == 16


# CP-HU02-08
def test_appointment_on_different_date(
    app,
    professional_id
):

    with app.app_context():

        add_appointment(
            professional_id,
            appointment_date=date(2026, 12, 1)
        )

        slots = get_available_slots(
            professional_id,
            TEST_DATE
        )

        assert "09:00" in slots
        assert len(slots) == 16


# CP-HU02-09
def test_lunch_break_is_excluded(
    app,
    professional_id
):

    with app.app_context():

        slots = get_available_slots(
            professional_id,
            TEST_DATE
        )

        assert "11:30" in slots
        assert "12:00" not in slots
        assert "12:30" not in slots
        assert "13:00" in slots


# CP-HU02-10
def test_working_hours_boundaries(
    app,
    professional_id
):

    with app.app_context():

        slots = get_available_slots(
            professional_id,
            TEST_DATE
        )

        assert slots[0] == "08:00"
        assert slots[-1] == "16:30"

        assert "07:30" not in slots
        assert "17:00" not in slots


# CP-HU02-11
def test_overlapping_appointment(
    app,
    professional_id
):

    with app.app_context():

        add_appointment(
            professional_id,
            start_time=time(9, 15)
        )

        slots = get_available_slots(
            professional_id,
            TEST_DATE
        )

        assert "09:00" not in slots
        assert "09:30" not in slots

        assert "08:30" in slots
        assert "10:00" in slots

        assert len(slots) == 14


# CP-HU02-12
def test_schedule_shorter_than_slot(app):

    with app.app_context():

        professional = Professional(
            name="Profesional horario reducido",
            specialty="Psicología",
            active=True
        )

        db.session.add(professional)
        db.session.flush()

        schedule = Schedule(
            professional_id=professional.id,
            weekday=1,
            start_time=time(8, 0),
            end_time=time(8, 15)
        )

        db.session.add(schedule)
        db.session.commit()

        assert get_available_slots(
            professional.id,
            TEST_DATE
        ) == []


# CP-HU02-13
def test_availability_requires_authentication(client):

    response = client.get(
        "/appointments/availability"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.location


# CP-HU02-14
def test_authenticated_availability_page(
    authenticated_client
):

    response = authenticated_client.get(
        "/appointments/availability"
    )

    assert response.status_code == 200

    assert (
        b"Consulta de disponibilidad"
        in response.data
    )


# CP-HU02-15
def test_valid_availability_form(
    authenticated_client,
    professional_id
):

    response = authenticated_client.post(
        "/appointments/availability",
        data={
            "professional_id": professional_id,
            "selected_date": "2026-11-24"
        }
    )

    assert response.status_code == 200

    assert b"Resultados de la consulta" in response.data
    assert b"08:00" in response.data
    assert b"16:30" in response.data
    assert b"12:30" not in response.data


# CP-HU02-16
def test_invalid_professional_form(
    authenticated_client
):

    response = authenticated_client.post(
        "/appointments/availability",
        data={
            "professional_id": 999999,
            "selected_date": "2026-11-24"
        }
    )

    assert response.status_code == 200
    assert b"Resultados de la consulta" not in response.data
    assert b"availability-error" in response.data


# CP-HU02-17
def test_invalid_date_form(
    authenticated_client,
    professional_id
):

    response = authenticated_client.post(
        "/appointments/availability",
        data={
            "professional_id": professional_id,
            "selected_date": "invalid-date"
        }
    )

    assert response.status_code == 200
    assert b"Resultados de la consulta" not in response.data
    assert b"availability-error" in response.data
