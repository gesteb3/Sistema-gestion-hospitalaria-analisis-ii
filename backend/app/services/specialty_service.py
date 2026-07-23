from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.specialty import Specialty
from app.repositories.specialty_repository import (
    get_specialty_by_id,
    get_specialty_by_name,
    list_specialties,
)
from app.schemas.specialty import (
    SpecialtyCreate,
    SpecialtyResponse,
    SpecialtyUpdate,
)


def specialty_to_response(
    specialty: Specialty,
) -> SpecialtyResponse:
    return SpecialtyResponse(
        especialidad_id=specialty.especialidad_id,
        nombre=specialty.nombre,
        descripcion=specialty.descripcion,
        activa=specialty.esta_activa,
        fecha_creacion=specialty.fecha_creacion,
    )


def get_specialty_or_404(
    database: Session,
    specialty_id: int,
) -> Specialty:
    specialty = get_specialty_by_id(
        database,
        specialty_id,
    )

    if specialty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Especialidad no encontrada.",
        )

    return specialty


def create_specialty(
    database: Session,
    payload: SpecialtyCreate,
) -> SpecialtyResponse:
    if get_specialty_by_name(database, payload.nombre):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La especialidad ya está registrada.",
        )

    specialty = Specialty(
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        estado=1,
    )

    database.add(specialty)

    try:
        database.commit()
        database.refresh(specialty)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar la especialidad.",
        ) from exc

    return specialty_to_response(specialty)


def read_specialties(
    database: Session,
    include_inactive: bool,
) -> list[SpecialtyResponse]:
    return [
        specialty_to_response(specialty)
        for specialty in list_specialties(
            database,
            include_inactive,
        )
    ]


def read_specialty(
    database: Session,
    specialty_id: int,
) -> SpecialtyResponse:
    return specialty_to_response(
        get_specialty_or_404(
            database,
            specialty_id,
        )
    )


def update_specialty(
    database: Session,
    specialty_id: int,
    payload: SpecialtyUpdate,
) -> SpecialtyResponse:
    specialty = get_specialty_or_404(
        database,
        specialty_id,
    )

    data = payload.model_dump(exclude_unset=True)

    if "nombre" in data:
        existing = get_specialty_by_name(
            database,
            data["nombre"],
        )

        if (
            existing is not None
            and existing.especialidad_id != specialty_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La especialidad ya está registrada.",
            )

    for field, value in data.items():
        setattr(specialty, field, value)

    database.commit()
    database.refresh(specialty)

    return specialty_to_response(specialty)


def deactivate_specialty(
    database: Session,
    specialty_id: int,
) -> str:
    specialty = get_specialty_or_404(
        database,
        specialty_id,
    )

    if not specialty.esta_activa:
        return "La especialidad ya se encontraba inactiva."

    specialty.estado = 0
    database.commit()

    return "Especialidad desactivada correctamente."


def reactivate_specialty(
    database: Session,
    specialty_id: int,
) -> SpecialtyResponse:
    specialty = get_specialty_or_404(
        database,
        specialty_id,
    )
    specialty.estado = 1
    database.commit()
    database.refresh(specialty)

    return specialty_to_response(specialty)
