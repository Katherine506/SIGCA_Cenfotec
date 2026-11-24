
from datetime import time

from app import create_app
from app.extensions import db
from app.models import Professional, Schedule


app = create_app()


def seed_professionals():

    professionals = [
        ("Dra. Ana Rodríguez", "Medicina general"),
        ("Lic. María Fernández", "Nutrición"),
        ("Lic. Carlos Vargas", "Psicología"),
        ("Lic. Laura Jiménez", "Fisioterapia"),
    ]

    with app.app_context():

        for name, specialty in professionals:

            professional = Professional.query.filter_by(
                name=name,
                specialty=specialty
            ).first()

            if professional is None:

                professional = Professional(
                    name=name,
                    specialty=specialty,
                    active=True
                )

                db.session.add(professional)
                db.session.flush()

            for weekday in range(5):

                periods = [
                    (time(8, 0), time(12, 0)),
                    (time(13, 0), time(17, 0))
                ]

                for start, end in periods:

                    existing = Schedule.query.filter_by(
                        professional_id=professional.id,
                        weekday=weekday,
                        start_time=start,
                        end_time=end
                    ).first()

                    if existing is None:

                        schedule = Schedule(
                            professional_id=professional.id,
                            weekday=weekday,
                            start_time=start,
                            end_time=end
                        )

                        db.session.add(schedule)

        db.session.commit()

        print("Datos de demostración creados correctamente.")
        print(f"Profesionales: {Professional.query.count()}")
        print(f"Horarios: {Schedule.query.count()}")


if __name__ == "__main__":
    seed_professionals()
