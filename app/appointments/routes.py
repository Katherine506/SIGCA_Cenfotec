
from flask import render_template
from flask_login import login_required

from app.appointments import appointments_bp
from app.appointments.forms import AvailabilityForm
from app.appointments.services import get_availability
from app.models import Professional
from app.extensions import db


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
