from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.specialty import Specialty


def get_specialty_by_id(
    database: Session,
    specialty_id: int,
) -> Specialty | None:
    return database.get(Specialty, specialty_id)


def get_specialty_by_name(
    database: Session,
    name: str,
) -> Specialty | None:
    statement = select(Specialty).where(
        func.lower(Specialty.nombre)
        == name.strip().lower()
    )
    return database.scalar(statement)


def get_specialties_by_ids(
    database: Session,
    specialty_ids: list[int],
) -> list[Specialty]:
    statement = (
        select(Specialty)
        .where(
            Specialty.especialidad_id.in_(specialty_ids),
            Specialty.estado == 1,
        )
        .order_by(Specialty.nombre)
    )
    return list(database.scalars(statement).all())


def list_specialties(
    database: Session,
    include_inactive: bool,
) -> list[Specialty]:
    statement = select(Specialty).order_by(
        Specialty.nombre
    )

    if not include_inactive:
        statement = statement.where(
            Specialty.estado == 1
        )

    return list(database.scalars(statement).all())
