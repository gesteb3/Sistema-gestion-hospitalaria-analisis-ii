from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.patient import Patient


def get_patient_by_id(
    database: Session,
    patient_id: int,
) -> Patient | None:
    statement = (
        select(Patient)
        .options(selectinload(Patient.responsables_legales))
        .where(Patient.paciente_id == patient_id)
    )
    return database.scalar(statement)


def get_patient_by_identification(
    database: Session,
    identification: str,
) -> Patient | None:
    statement = (
        select(Patient)
        .options(selectinload(Patient.responsables_legales))
        .where(
            func.lower(Patient.identificacion)
            == identification.strip().lower()
        )
    )
    return database.scalar(statement)


def list_patients(
    database: Session,
    search: str | None,
    page: int,
    page_size: int,
    include_inactive: bool,
) -> tuple[list[Patient], int]:
    filters = []

    if not include_inactive:
        filters.append(Patient.estado == 1)

    if search:
        pattern = f"%{search.strip().lower()}%"
        filters.append(
            or_(
                func.lower(Patient.numero_expediente).like(pattern),
                func.lower(Patient.nombres).like(pattern),
                func.lower(Patient.apellidos).like(pattern),
                func.lower(Patient.identificacion).like(pattern),
            )
        )

    count_statement = select(func.count(Patient.paciente_id))

    if filters:
        count_statement = count_statement.where(*filters)

    total = int(database.scalar(count_statement) or 0)

    statement = (
        select(Patient)
        .options(selectinload(Patient.responsables_legales))
        .order_by(Patient.paciente_id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if filters:
        statement = statement.where(*filters)

    patients = list(database.scalars(statement).all())
    return patients, total
