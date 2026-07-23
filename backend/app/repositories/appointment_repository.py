from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient


APPOINTMENT_LOAD_OPTIONS = (
    joinedload(Appointment.paciente),
    joinedload(Appointment.medico).selectinload(
        Doctor.especialidades
    ),
)


def get_appointment_by_id(
    database: Session,
    appointment_id: int,
) -> Appointment | None:
    statement = (
        select(Appointment)
        .options(*APPOINTMENT_LOAD_OPTIONS)
        .where(Appointment.cita_id == appointment_id)
    )
    return database.scalar(statement)


def list_appointments(
    database: Session,
    patient_id: int | None,
    doctor_id: int | None,
    appointment_status: str | None,
    date_from: date | None,
    date_to: date | None,
    page: int,
    page_size: int,
) -> tuple[list[Appointment], int]:
    filters = []

    if patient_id is not None:
        filters.append(
            Appointment.paciente_id == patient_id
        )

    if doctor_id is not None:
        filters.append(
            Appointment.medico_id == doctor_id
        )

    if appointment_status is not None:
        filters.append(
            Appointment.estado == appointment_status
        )

    if date_from is not None:
        filters.append(
            Appointment.fecha >= date_from
        )

    if date_to is not None:
        filters.append(
            Appointment.fecha <= date_to
        )

    count_statement = select(
        func.count(Appointment.cita_id)
    )

    if filters:
        count_statement = count_statement.where(*filters)

    total = int(database.scalar(count_statement) or 0)

    statement = (
        select(Appointment)
        .options(*APPOINTMENT_LOAD_OPTIONS)
        .order_by(
            Appointment.fecha.desc(),
            Appointment.hora.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if filters:
        statement = statement.where(*filters)

    appointments = list(
        database.scalars(statement).unique().all()
    )

    return appointments, total


def list_active_appointments_for_doctor_date(
    database: Session,
    doctor_id: int,
    appointment_date: date,
    exclude_appointment_id: int | None = None,
) -> list[Appointment]:
    statement = select(Appointment).where(
        Appointment.medico_id == doctor_id,
        Appointment.fecha == appointment_date,
        Appointment.estado.in_(
            ["PROGRAMADA", "CONFIRMADA"]
        ),
    )

    if exclude_appointment_id is not None:
        statement = statement.where(
            Appointment.cita_id
            != exclude_appointment_id
        )

    return list(database.scalars(statement).all())


def list_active_appointments_for_patient_date(
    database: Session,
    patient_id: int,
    appointment_date: date,
    exclude_appointment_id: int | None = None,
) -> list[Appointment]:
    statement = select(Appointment).where(
        Appointment.paciente_id == patient_id,
        Appointment.fecha == appointment_date,
        Appointment.estado.in_(
            ["PROGRAMADA", "CONFIRMADA"]
        ),
    )

    if exclude_appointment_id is not None:
        statement = statement.where(
            Appointment.cita_id
            != exclude_appointment_id
        )

    return list(database.scalars(statement).all())
