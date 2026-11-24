from datetime import date, time, timedelta

import pytest

from app.extensions import db
from app.models import Professional, Schedule, Appointment

from app.appointments.services import (
    register_appointment,
    get_available_slots,
    AppointmentError
)


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
            name="Profesional de prueba",
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


def create_test_appointment(
    professional_id,
    appointment_date,
    patient_name="Paciente de prueba",
    start_time="09:00"
):

    return register_appointment(
        patient_name=patient_name,
        professional_id=professional_id,
        appointment_date=appointment_date,
        start_time=start_time
    )


# CP-HU03-01
def test_register_valid_appointment(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        appointment = create_test_appointment(
            professional_id,
            appointment_date
        )

        appointment_id = appointment.id

        db.session.expire_all()

        saved = db.session.get(
            Appointment,
            appointment_id
        )

        assert saved is not None
        assert saved.patient_name == "Paciente de prueba"
        assert saved.professional_id == professional_id
        assert saved.date == appointment_date
        assert saved.start_time == time(9, 0)
        assert saved.status == "activa"


# CP-HU03-02
def test_patient_name_is_normalized(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        appointment = create_test_appointment(
            professional_id,
            appointment_date,
            patient_name="  Paciente de prueba  "
        )

        assert appointment.patient_name == "Paciente de prueba"


# CP-HU03-03
def test_empty_patient_name(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        with pytest.raises(
            AppointmentError,
            match="obligatorio"
        ):

            create_test_appointment(
                professional_id,
                appointment_date,
                patient_name=""
            )

        assert Appointment.query.count() == 0


# CP-HU03-04
def test_whitespace_patient_name(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        with pytest.raises(
            AppointmentError,
            match="obligatorio"
        ):

            create_test_appointment(
                professional_id,
                appointment_date,
                patient_name="     "
            )


# CP-HU03-05
def test_patient_name_maximum_length(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        appointment = create_test_appointment(
            professional_id,
            appointment_date,
            patient_name="A" * 120
        )

        assert len(appointment.patient_name) == 120


# CP-HU03-06
def test_patient_name_exceeds_maximum_length(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        with pytest.raises(
            AppointmentError,
            match="120 caracteres"
        ):

            create_test_appointment(
                professional_id,
                appointment_date,
                patient_name="A" * 121
            )


# CP-HU03-07
def test_past_appointment_date(
    app,
    professional_id
):

    with app.app_context():

        with pytest.raises(
            AppointmentError,
            match="fechas anteriores"
        ):

            create_test_appointment(
                professional_id,
                date.today() - timedelta(days=1)
            )


# CP-HU03-08
def test_invalid_appointment_date(
    app,
    professional_id
):

    with app.app_context():

        with pytest.raises(
            AppointmentError,
            match="fecha de la cita no es válida"
        ):

            create_test_appointment(
                professional_id,
                "invalid-date"
            )


# CP-HU03-09
def test_nonexistent_professional(
    app,
    appointment_date
):

    with app.app_context():

        with pytest.raises(
            AppointmentError,
            match="profesional seleccionado"
        ):

            create_test_appointment(
                999999,
                appointment_date
            )


# CP-HU03-10
def test_inactive_professional(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        professional = db.session.get(
            Professional,
            professional_id
        )

        professional.active = False
        db.session.commit()

        with pytest.raises(
            AppointmentError,
            match="profesional seleccionado"
        ):

            create_test_appointment(
                professional_id,
                appointment_date
            )


# CP-HU03-11
def test_invalid_time_format(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        with pytest.raises(
            AppointmentError,
            match="horario seleccionado no es válido"
        ):

            create_test_appointment(
                professional_id,
                appointment_date,
                start_time="25:99"
            )


# CP-HU03-12
def test_appointment_outside_working_hours(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        with pytest.raises(
            AppointmentError,
            match="horario seleccionado no está disponible"
        ):

            create_test_appointment(
                professional_id,
                appointment_date,
                start_time="17:00"
            )


# CP-HU03-13
def test_appointment_during_lunch_break(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        with pytest.raises(
            AppointmentError,
            match="horario seleccionado no está disponible"
        ):

            create_test_appointment(
                professional_id,
                appointment_date,
                start_time="12:30"
            )


# CP-HU03-14
def test_duplicate_appointment_is_rejected(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        create_test_appointment(
            professional_id,
            appointment_date
        )

        with pytest.raises(
            AppointmentError,
            match="horario seleccionado no está disponible"
        ):

            create_test_appointment(
                professional_id,
                appointment_date,
                patient_name="Segundo paciente"
            )

        assert Appointment.query.count() == 1


# CP-HU03-15
def test_overlapping_appointment_is_rejected(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        existing = Appointment(
            professional_id=professional_id,
            patient_name="Paciente existente",
            date=appointment_date,
            start_time=time(9, 15),
            status="activa"
        )

        db.session.add(existing)
        db.session.commit()

        with pytest.raises(AppointmentError):

            create_test_appointment(
                professional_id,
                appointment_date,
                start_time="09:30"
            )

        assert Appointment.query.count() == 1


# CP-HU03-16
def test_cancelled_slot_can_be_booked(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        existing = Appointment(
            professional_id=professional_id,
            patient_name="Paciente anterior",
            date=appointment_date,
            start_time=time(9, 0),
            status="cancelada"
        )

        db.session.add(existing)
        db.session.commit()

        appointment = create_test_appointment(
            professional_id,
            appointment_date
        )

        assert appointment.status == "activa"
        assert Appointment.query.count() == 2


# CP-HU03-17
def test_same_time_different_professionals(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        other = Professional(
            name="Segundo profesional",
            specialty="Nutrición",
            active=True
        )

        db.session.add(other)
        db.session.flush()

        schedule = Schedule(
            professional_id=other.id,
            weekday=appointment_date.weekday(),
            start_time=time(8, 0),
            end_time=time(12, 0)
        )

        db.session.add(schedule)
        db.session.commit()

        first = create_test_appointment(
            professional_id,
            appointment_date
        )

        second = create_test_appointment(
            other.id,
            appointment_date
        )

        assert first.professional_id != second.professional_id
        assert first.start_time == second.start_time
        assert Appointment.query.count() == 2


# CP-HU03-18
def test_registration_updates_availability(
    app,
    professional_id,
    appointment_date
):

    with app.app_context():

        before = get_available_slots(
            professional_id,
            appointment_date
        )

        assert len(before) == 16

        create_test_appointment(
            professional_id,
            appointment_date
        )

        after = get_available_slots(
            professional_id,
            appointment_date
        )

        assert len(after) == 15
        assert "09:00" not in after


# CP-HU03-19
def test_registration_requires_authentication(client):

    response = client.get(
        "/appointments/register"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.location


# CP-HU03-20
def test_authenticated_registration_page(
    authenticated_client
):

    response = authenticated_client.get(
        "/appointments/register"
    )

    assert response.status_code == 200
    assert b"Registro de citas" in response.data


# CP-HU03-21
def test_register_appointment_from_form(
    app,
    authenticated_client,
    professional_id,
    appointment_date
):

    response = authenticated_client.post(
        "/appointments/register",
        data={
            "patient_name": "Paciente formulario",
            "professional_id": professional_id,
            "selected_date": appointment_date.isoformat(),
            "start_time": "09:00"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"Cita registrada correctamente"
        in response.data
    )

    with app.app_context():

        appointment = Appointment.query.filter_by(
            patient_name="Paciente formulario"
        ).first()

        assert appointment is not None
        assert appointment.status == "activa"
        assert appointment.start_time == time(9, 0)


# CP-HU03-22
def test_available_slots_endpoint(
    authenticated_client,
    professional_id,
    appointment_date
):

    response = authenticated_client.get(
        "/appointments/available-slots",
        query_string={
            "professional_id": professional_id,
            "date": appointment_date.isoformat()
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["slots"]) == 16
    assert "09:00" in data["slots"]
    assert "12:30" not in data["slots"]


# CP-HU03-23
def test_available_slots_missing_parameters(
    authenticated_client
):

    response = authenticated_client.get(
        "/appointments/available-slots"
    )

    assert response.status_code == 400
    assert response.get_json()["slots"] == []


# CP-HU03-24
def test_available_slots_invalid_date(
    authenticated_client,
    professional_id
):

    response = authenticated_client.get(
        "/appointments/available-slots",
        query_string={
            "professional_id": professional_id,
            "date": "invalid-date"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["slots"] == []


# CP-HU03-25
def test_available_slots_requires_authentication(
    client
):

    response = client.get(
        "/appointments/available-slots"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.location