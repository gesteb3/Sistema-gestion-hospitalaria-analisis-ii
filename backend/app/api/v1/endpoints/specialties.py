from fastapi import APIRouter, status

from app.api.dependencies import (
    DatabaseDependency,
    DoctorReaderDependency,
    DoctorWriterDependency,
)
from app.schemas.doctor import DoctorMessageResponse
from app.schemas.specialty import (
    SpecialtyCreate,
    SpecialtyResponse,
    SpecialtyUpdate,
)
from app.services.specialty_service import (
    create_specialty,
    deactivate_specialty,
    reactivate_specialty,
    read_specialties,
    read_specialty,
    update_specialty,
)


router = APIRouter(
    prefix="/specialties",
    tags=["Especialidades"],
)


@router.get(
    "",
    response_model=list[SpecialtyResponse],
)
def list_registered_specialties(
    database: DatabaseDependency,
    _: DoctorReaderDependency,
    include_inactive: bool = False,
) -> list[SpecialtyResponse]:
    return read_specialties(
        database,
        include_inactive,
    )


@router.get(
    "/{specialty_id}",
    response_model=SpecialtyResponse,
)
def get_registered_specialty(
    specialty_id: int,
    database: DatabaseDependency,
    _: DoctorReaderDependency,
) -> SpecialtyResponse:
    return read_specialty(
        database,
        specialty_id,
    )


@router.post(
    "",
    response_model=SpecialtyResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_specialty(
    payload: SpecialtyCreate,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> SpecialtyResponse:
    return create_specialty(
        database,
        payload,
    )


@router.put(
    "/{specialty_id}",
    response_model=SpecialtyResponse,
)
def modify_specialty(
    specialty_id: int,
    payload: SpecialtyUpdate,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> SpecialtyResponse:
    return update_specialty(
        database,
        specialty_id,
        payload,
    )


@router.delete(
    "/{specialty_id}",
    response_model=DoctorMessageResponse,
)
def remove_specialty(
    specialty_id: int,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> DoctorMessageResponse:
    return DoctorMessageResponse(
        message=deactivate_specialty(
            database,
            specialty_id,
        )
    )


@router.patch(
    "/{specialty_id}/reactivate",
    response_model=SpecialtyResponse,
)
def restore_specialty(
    specialty_id: int,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> SpecialtyResponse:
    return reactivate_specialty(
        database,
        specialty_id,
    )
