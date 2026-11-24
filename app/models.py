
from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app.extensions import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(30),
        nullable=False,
        default="recepcionista"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

class Professional(db.Model):

    __tablename__ = "professionals"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    schedules = db.relationship(
        "Schedule",
        back_populates="professional",
        cascade="all, delete-orphan"
    )

    appointments = db.relationship(
        "Appointment",
        back_populates="professional"
    )


class Schedule(db.Model):

    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)

    professional_id = db.Column(
        db.Integer,
        db.ForeignKey("professionals.id"),
        nullable=False
    )

    weekday = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    professional = db.relationship(
        "Professional",
        back_populates="schedules"
    )

    __table_args__ = (
        db.CheckConstraint(
            "weekday >= 0 AND weekday <= 6",
            name="valid_weekday"
        ),
        db.CheckConstraint(
            "start_time < end_time",
            name="valid_schedule_time"
        ),
        db.UniqueConstraint(
            "professional_id",
            "weekday",
            "start_time",
            "end_time",
            name="unique_professional_schedule"
        ),
    )


class Appointment(db.Model):

    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)

    professional_id = db.Column(
        db.Integer,
        db.ForeignKey("professionals.id"),
        nullable=False
    )

    patient_name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)

    status = db.Column(
        db.String(20),
        default="activa",
        nullable=False
    )

    professional = db.relationship(
        "Professional",
        back_populates="appointments"
    )

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('activa', 'cancelada')",
            name="valid_appointment_status"
        ),
        db.Index(
            "uq_active_appointment_slot",
            "professional_id",
            "date",
            "start_time",
            unique=True,
            sqlite_where=db.text("status = 'activa'")
        ),
    )
