from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import (
    ClinicalReaderDependency,
    ClinicalWriterDependency,
    DatabaseDependency,
    VitalSignsWriterDependency,
)
from app.schemas.clinical import (
    ClinicalHistoryResponse,
    ClinicalHistoryUpdate,
    ConsultationCreate,
    ConsultationListResponse,
    ConsultationResponse,
    ConsultationUpdate,
    DiagnosisInput,
    TreatmentInput,
    VitalSignsInput,
)
from app.services.clinical_service import (
    add_diagnosis,
    add_treatment,
    create_consultation,
    read_consultation,
    read_consultations,
    read_history,
    save_vital_signs,
    update_consultation,
    update_history,
)


history_router = APIRouter(
    prefix="/clinical-histories",
    tags=["Historial clínico"],
)

consultation_router = APIRouter(
    prefix="/consultations",
    tags=["Consultas clínicas"],
)


@history_router.get(
    "/patient/{patient_id}",
    response_model=ClinicalHistoryResponse,
)
def get_patient_history(
    patient_id: int,
    database: DatabaseDependency,
    _: ClinicalReaderDependency,
) -> ClinicalHistoryResponse:
    return read_history(
        database,
        patient_id,
    )


@history_router.put(
    "/patient/{patient_id}",
    response_model=ClinicalHistoryResponse,
)
def modify_patient_history(
    patient_id: int,
    payload: ClinicalHistoryUpdate,
    database: DatabaseDependency,
    _: ClinicalWriterDependency,
) -> ClinicalHistoryResponse:
    return update_history(
        database,
        patient_id,
        payload,
    )


@consultation_router.post(
    "",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_consultation(
    payload: ConsultationCreate,
    database: DatabaseDependency,
    _: ClinicalWriterDependency,
) -> ConsultationResponse:
    return create_consultation(
        database,
        payload,
    )


@consultation_router.get(
    "",
    response_model=ConsultationListResponse,
)
def list_clinical_consultations(
    database: DatabaseDependency,
    _: ClinicalReaderDependency,
    patient_id: int | None = None,
    doctor_id: int | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> ConsultationListResponse:
    return read_consultations(
        database=database,
        patient_id=patient_id,
        doctor_id=doctor_id,
        page=page,
        page_size=page_size,
    )


@consultation_router.get(
    "/{consultation_id}",
    response_model=ConsultationResponse,
)
def get_clinical_consultation(
    consultation_id: int,
    database: DatabaseDependency,
    _: ClinicalReaderDependency,
) -> ConsultationResponse:
    return read_consultation(
        database,
        consultation_id,
    )


@consultation_router.put(
    "/{consultation_id}",
    response_model=ConsultationResponse,
)
def modify_clinical_consultation(
    consultation_id: int,
    payload: ConsultationUpdate,
    database: DatabaseDependency,
    _: ClinicalWriterDependency,
) -> ConsultationResponse:
    return update_consultation(
        database,
        consultation_id,
        payload,
    )


@consultation_router.put(
    "/{consultation_id}/vital-signs",
    response_model=ConsultationResponse,
)
def register_or_update_vital_signs(
    consultation_id: int,
    payload: VitalSignsInput,
    database: DatabaseDependency,
    _: VitalSignsWriterDependency,
) -> ConsultationResponse:
    return save_vital_signs(
        database,
        consultation_id,
        payload,
    )


@consultation_router.post(
    "/{consultation_id}/diagnoses",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_diagnosis(
    consultation_id: int,
    payload: DiagnosisInput,
    database: DatabaseDependency,
    _: ClinicalWriterDependency,
) -> ConsultationResponse:
    return add_diagnosis(
        database,
        consultation_id,
        payload,
    )


@consultation_router.post(
    "/{consultation_id}/treatments",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_treatment(
    consultation_id: int,
    payload: TreatmentInput,
    database: DatabaseDependency,
    _: ClinicalWriterDependency,
) -> ConsultationResponse:
    return add_treatment(
        database,
        consultation_id,
        payload,
    )
