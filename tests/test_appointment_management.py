from datetime import date, datetime, time, timedelta

import pytest

from app.extensions import db

from app.models import (
    Professional,
    Schedule,
    Appointment
)

from app.appointments.services import (
    AppointmentError,
    register_appointment,
    get_appointments,
    get_available_slots,
    cancel_appointment,
    reschedule_appointment
)


# =========================================
# Fixtures
# =========================================

@pytest.fixture
def appointment_date():

    selected_date = date.today() + timedelta(days=1)

    while selected_date.weekday() >= 5:
        selected_date += timedelta(days=1)

    return selected_date


@pytest.fixture
def professional_id(app, appointment_date):

    with app.app_context():

        professional = Professional(
            name="Dra. Profesional de prueba",
            specialty="Medicina general",
            active=True
        )

        db.session.add(professional)
        db.session.flush()

        schedules = [
            Schedule(
                professional_id=professional.id,
                weekday=appointment_date.weekday(),
                start_time=time(8, 0),
                end_time=time(12, 0)
            ),
            Schedule(
                professional_id=professional.id,
                weekday=appointment_date.weekday(),
                start_time=time(13, 0),
                end_time=time(17, 0)
            )
        ]

        db.session.add_all(schedules)
        db.session.commit()

        return professional.id


@pytest.fixture
def appointment_id(app, professional_id, appointment_date):

    with app.app_context():

        appointment = register_appointment(
            patient_name="Paciente de prueba",
            professional_id=professional_id,
            appointment_date=appointment_date,
            start_time="09:00"
        )

        return appointment.id


@pytest.fixture
def authenticated_client(client):

    response = client.post(
        "/auth/login",
        data={
            "email": "test@example.com",
            "password": "test-password"
        }
    )

    assert response.status_code == 302
    assert client.get("/").status_code == 200

    return client


# =========================================
# HU-04 - Consulta y búsqueda de citas
# =========================================

def test_get_appointments_empty(app):

    with app.app_context():

        assert get_appointments() == []


def test_get_appointments_returns_registered_appointment(
    app, appointment_id
):

    with app.app_context():

        appointments = get_appointments()

        assert len(appointments) == 1
        assert appointments[0].id == appointment_id


def test_search_appointment_by_patient(
    app, appointment_id
):

    with app.app_context():

        appointments = get_appointments(
            search="Paciente"
        )

        assert len(appointments) == 1
        assert appointments[0].id == appointment_id


def test_search_appointment_without_matches(
    app, appointment_id
):

    with app.app_context():

        appointments = get_appointments(
            search="Paciente inexistente"
        )

        assert appointments == []


def test_filter_active_appointments(
    app, appointment_id
):

    with app.app_context():

        appointments = get_appointments(
            status="activa"
        )

        assert len(appointments) == 1
        assert appointments[0].status == "activa"


def test_filter_cancelled_appointments(
    app, appointment_id
):

    with app.app_context():

        cancel_appointment(appointment_id)

        appointments = get_appointments(
            status="cancelada"
        )

        assert len(appointments) == 1
        assert appointments[0].status == "cancelada"


# =========================================
# HU-04 - Cancelación de citas
# =========================================

def test_cancel_appointment_success(
    app, appointment_id
):

    with app.app_context():

        appointment = cancel_appointment(
            appointment_id
        )

        assert appointment.status == "cancelada"


def test_cancel_appointment_persists_status(
    app, appointment_id
):

    with app.app_context():

        cancel_appointment(appointment_id)

        db.session.remove()

        appointment = db.session.get(
            Appointment,
            appointment_id
        )

        assert appointment.status == "cancelada"


def test_cancel_appointment_releases_slot(
    app, appointment_id,
    professional_id, appointment_date
):

    with app.app_context():

        assert "09:00" not in get_available_slots(
            professional_id,
            appointment_date
        )

        cancel_appointment(appointment_id)

        assert "09:00" in get_available_slots(
            professional_id,
            appointment_date
        )


def test_cancel_nonexistent_appointment(app):

    with app.app_context():

        with pytest.raises(AppointmentError):

            cancel_appointment(999999)


def test_cancel_already_cancelled_appointment(
    app, appointment_id
):

    with app.app_context():

        cancel_appointment(appointment_id)

        with pytest.raises(AppointmentError):

            cancel_appointment(appointment_id)


def test_cancelled_appointment_is_not_deleted(
    app, appointment_id
):

    with app.app_context():

        cancel_appointment(appointment_id)

        appointment = db.session.get(
            Appointment,
            appointment_id
        )

        assert appointment is not None
        assert appointment.status == "cancelada"


# =========================================
# HU-04 - Reprogramación de citas
# =========================================

def test_reschedule_appointment_success(
    app, appointment_id, appointment_date
):

    with app.app_context():

        appointment = reschedule_appointment(
            appointment_id,
            appointment_date,
            "10:30"
        )

        assert appointment.start_time == time(10, 30)
        assert appointment.status == "activa"


def test_reschedule_releases_original_slot(
    app, appointment_id,
    professional_id, appointment_date
):

    with app.app_context():

        reschedule_appointment(
            appointment_id,
            appointment_date,
            "10:30"
        )

        slots = get_available_slots(
            professional_id,
            appointment_date
        )

        assert "09:00" in slots


def test_reschedule_occupies_new_slot(
    app, appointment_id,
    professional_id, appointment_date
):

    with app.app_context():

        reschedule_appointment(
            appointment_id,
            appointment_date,
            "10:30"
        )

        slots = get_available_slots(
            professional_id,
            appointment_date
        )

        assert "10:30" not in slots


def test_reschedule_preserves_patient_and_professional(
    app, appointment_id,
    professional_id, appointment_date
):

    with app.app_context():

        appointment = reschedule_appointment(
            appointment_id,
            appointment_date,
            "10:30"
        )

        assert appointment.id == appointment_id

        assert appointment.patient_name == (
            "Paciente de prueba"
        )

        assert appointment.professional_id == (
            professional_id
        )


def test_reschedule_nonexistent_appointment(
    app, appointment_date
):

    with app.app_context():

        with pytest.raises(AppointmentError):

            reschedule_appointment(
                999999,
                appointment_date,
                "10:30"
            )


def test_reschedule_cancelled_appointment(
    app, appointment_id, appointment_date
):

    with app.app_context():

        cancel_appointment(appointment_id)

        with pytest.raises(AppointmentError):

            reschedule_appointment(
                appointment_id,
                appointment_date,
                "10:30"
            )


def test_reschedule_to_past_date(
    app, appointment_id
):

    with app.app_context():

        past_date = date.today() - timedelta(days=1)

        with pytest.raises(AppointmentError):

            reschedule_appointment(
                appointment_id,
                past_date,
                "10:30"
            )


def test_reschedule_invalid_date(
    app, appointment_id
):

    with app.app_context():

        with pytest.raises(AppointmentError):

            reschedule_appointment(
                appointment_id,
                "fecha-invalida",
                "10:30"
            )


def test_reschedule_invalid_time(
    app, appointment_id, appointment_date
):

    with app.app_context():

        with pytest.raises(AppointmentError):

            reschedule_appointment(
                appointment_id,
                appointment_date,
                "25:00"
            )


def test_reschedule_to_same_slot(
    app, appointment_id, appointment_date
):

    with app.app_context():

        with pytest.raises(AppointmentError):

            reschedule_appointment(
                appointment_id,
                appointment_date,
                "09:00"
            )


def test_reschedule_to_occupied_slot(
    app, appointment_id,
    professional_id, appointment_date
):

    with app.app_context():

        register_appointment(
            patient_name="Segundo paciente",
            professional_id=professional_id,
            appointment_date=appointment_date,
            start_time="10:30"
        )

        with pytest.raises(AppointmentError):

            reschedule_appointment(
                appointment_id,
                appointment_date,
                "10:30"
            )

        appointment = db.session.get(
            Appointment,
            appointment_id
        )

        assert appointment.start_time == time(9, 0)
        assert appointment.status == "activa"


def test_reschedule_outside_working_hours(
    app, appointment_id, appointment_date
):

    with app.app_context():

        with pytest.raises(AppointmentError):

            reschedule_appointment(
                appointment_id,
                appointment_date,
                "17:00"
            )


# =========================================
# HU-04 - Seguridad y rutas HTTP
# =========================================

def test_manage_requires_authentication(client):

    response = client.get(
        "/appointments/manage"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_manage_authenticated(
    authenticated_client, appointment_id
):

    response = authenticated_client.get(
        "/appointments/manage"
    )

    assert response.status_code == 200
    assert b"Paciente de prueba" in response.data


def test_reschedule_requires_authentication(
    client, appointment_id
):

    response = client.get(
        f"/appointments/{appointment_id}/reschedule"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_reschedule_post_success(
    app, authenticated_client,
    appointment_id, appointment_date
):

    response = authenticated_client.post(
        f"/appointments/{appointment_id}/reschedule",
        data={
            "selected_date": appointment_date.isoformat(),
            "start_time": "10:30"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"Cita reprogramada correctamente"
        in response.data
    )

    with app.app_context():

        appointment = db.session.get(
            Appointment,
            appointment_id
        )

        assert appointment.start_time == time(10, 30)


def test_cancel_post_success(
    app, authenticated_client, appointment_id
):

    response = authenticated_client.post(
        f"/appointments/{appointment_id}/cancel",
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"Cita cancelada correctamente"
        in response.data
    )

    with app.app_context():

        appointment = db.session.get(
            Appointment,
            appointment_id
        )

        assert appointment.status == "cancelada"


def test_cancel_rejects_get_method(
    authenticated_client, appointment_id
):

    response = authenticated_client.get(
        f"/appointments/{appointment_id}/cancel"
    )

    assert response.status_code == 405