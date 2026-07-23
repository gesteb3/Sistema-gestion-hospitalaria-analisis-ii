from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from app.models.specialty import Specialty


DOCTOR_LOAD_OPTIONS = (
    selectinload(Doctor.especialidades),
    selectinload(Doctor.horarios),
)


def get_doctor_by_id(
    database: Session,
    doctor_id: int,
) -> Doctor | None:
    statement = (
        select(Doctor)
        .options(*DOCTOR_LOAD_OPTIONS)
        .where(Doctor.medico_id == doctor_id)
    )
    return database.scalar(statement)


def get_doctor_by_license(
    database: Session,
    license_number: str,
) -> Doctor | None:
    statement = (
        select(Doctor)
        .options(*DOCTOR_LOAD_OPTIONS)
        .where(
            func.lower(Doctor.numero_colegiado)
            == license_number.strip().lower()
        )
    )
    return database.scalar(statement)


def get_doctor_by_email(
    database: Session,
    email: str,
) -> Doctor | None:
    statement = (
        select(Doctor)
        .options(*DOCTOR_LOAD_OPTIONS)
        .where(
            func.lower(Doctor.correo)
            == email.strip().lower()
        )
    )
    return database.scalar(statement)


def list_doctors(
    database: Session,
    search: str | None,
    specialty_id: int | None,
    page: int,
    page_size: int,
    include_inactive: bool,
) -> tuple[list[Doctor], int]:
    filters = []

    if not include_inactive:
        filters.append(Doctor.estado == 1)

    if search:
        pattern = f"%{search.strip().lower()}%"
        filters.append(
            or_(
                func.lower(Doctor.nombres).like(pattern),
                func.lower(Doctor.apellidos).like(pattern),
                func.lower(Doctor.numero_colegiado).like(pattern),
                func.lower(Doctor.correo).like(pattern),
            )
        )

    base_statement = select(Doctor)
    count_statement = select(
        func.count(func.distinct(Doctor.medico_id))
    )

    if specialty_id is not None:
        base_statement = base_statement.join(
            Doctor.especialidades
        )
        count_statement = count_statement.join(
            Doctor.especialidades
        )
        filters.append(
            Specialty.especialidad_id == specialty_id
        )

    if filters:
        base_statement = base_statement.where(*filters)
        count_statement = count_statement.where(*filters)

    total = int(database.scalar(count_statement) or 0)

    statement = (
        base_statement
        .options(*DOCTOR_LOAD_OPTIONS)
        .order_by(Doctor.apellidos, Doctor.nombres)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    doctors = list(
        database.scalars(statement).unique().all()
    )
    return doctors, total


def get_schedule_by_id(
    database: Session,
    schedule_id: int,
) -> DoctorSchedule | None:
    return database.get(
        DoctorSchedule,
        schedule_id,
    )


def list_active_schedules_for_day(
    database: Session,
    doctor_id: int,
    day_number: int,
    exclude_schedule_id: int | None = None,
) -> list[DoctorSchedule]:
    statement = select(DoctorSchedule).where(
        DoctorSchedule.medico_id == doctor_id,
        DoctorSchedule.dia_semana == day_number,
        DoctorSchedule.estado == 1,
    )

    if exclude_schedule_id is not None:
        statement = statement.where(
            DoctorSchedule.horario_id
            != exclude_schedule_id
        )

    return list(database.scalars(statement).all())
