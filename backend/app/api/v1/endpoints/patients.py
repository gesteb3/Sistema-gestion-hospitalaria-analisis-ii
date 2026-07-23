from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import (
    DatabaseDependency,
    PatientReaderDependency,
    PatientWriterDependency,
)
from app.schemas.patient import (
    MessageResponse,
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.services.patient_service import (
    create_patient,
    deactivate_patient,
    reactivate_patient,
    read_patient,
    read_patients,
    update_patient,
)


router = APIRouter(
    prefix="/patients",
    tags=["Pacientes"],
)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_patient(
    payload: PatientCreate,
    database: DatabaseDependency,
    _: PatientWriterDependency,
) -> PatientResponse:
    return create_patient(database, payload)


@router.get(
    "",
    response_model=PatientListResponse,
)
def list_registered_patients(
    database: DatabaseDependency,
    _: PatientReaderDependency,
    search: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
            description=(
                "Busca por expediente, nombres, apellidos "
                "o identificación."
            ),
        ),
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    include_inactive: bool = False,
) -> PatientListResponse:
    return read_patients(
        database=database,
        search=search,
        page=page,
        page_size=page_size,
        include_inactive=include_inactive,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_registered_patient(
    patient_id: int,
    database: DatabaseDependency,
    _: PatientReaderDependency,
) -> PatientResponse:
    return read_patient(
        database,
        patient_id,
    )


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
)
def modify_patient(
    patient_id: int,
    payload: PatientUpdate,
    database: DatabaseDependency,
    _: PatientWriterDependency,
) -> PatientResponse:
    return update_patient(
        database,
        patient_id,
        payload,
    )


@router.delete(
    "/{patient_id}",
    response_model=MessageResponse,
)
def remove_patient(
    patient_id: int,
    database: DatabaseDependency,
    _: PatientWriterDependency,
) -> MessageResponse:
    message = deactivate_patient(
        database,
        patient_id,
    )
    return MessageResponse(message=message)


@router.patch(
    "/{patient_id}/reactivate",
    response_model=PatientResponse,
)
def restore_patient(
    patient_id: int,
    database: DatabaseDependency,
    _: PatientWriterDependency,
) -> PatientResponse:
    return reactivate_patient(
        database,
        patient_id,
    )
