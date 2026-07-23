from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import (
    DatabaseDependency,
    PharmacyReaderDependency,
    PharmacyWriterDependency,
    PrescriptionWriterDependency,
)
from app.schemas.pharmacy import (
    InventoryMovementResponse,
    MedicationCreate,
    MedicationListResponse,
    MedicationResponse,
    MedicationUpdate,
    PrescriptionCancel,
    PrescriptionCreate,
    PrescriptionListResponse,
    PrescriptionResponse,
    StockMovementCreate,
)
from app.services.pharmacy_service import (
    cancel_prescription,
    create_medication,
    create_prescription,
    dispense_prescription,
    read_medication,
    read_medications,
    read_prescription,
    read_prescriptions,
    register_stock_movement,
    update_medication,
)


medication_router = APIRouter(
    prefix="/medications",
    tags=["Medicamentos"],
)

prescription_router = APIRouter(
    prefix="/prescriptions",
    tags=["Recetas"],
)


@medication_router.post(
    "",
    response_model=MedicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_medication(
    payload: MedicationCreate,
    database: DatabaseDependency,
    _: PharmacyWriterDependency,
) -> MedicationResponse:
    return create_medication(
        database,
        payload,
    )


@medication_router.get(
    "",
    response_model=MedicationListResponse,
)
def list_registered_medications(
    database: DatabaseDependency,
    _: PharmacyReaderDependency,
    search: Annotated[
        str | None,
        Query(min_length=1, max_length=100),
    ] = None,
    low_stock: bool | None = None,
    include_inactive: bool = False,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> MedicationListResponse:
    return read_medications(
        database=database,
        search=search,
        low_stock=low_stock,
        include_inactive=include_inactive,
        page=page,
        page_size=page_size,
    )


@medication_router.get(
    "/{medication_id}",
    response_model=MedicationResponse,
)
def get_registered_medication(
    medication_id: int,
    database: DatabaseDependency,
    _: PharmacyReaderDependency,
) -> MedicationResponse:
    return read_medication(
        database,
        medication_id,
    )


@medication_router.put(
    "/{medication_id}",
    response_model=MedicationResponse,
)
def modify_medication(
    medication_id: int,
    payload: MedicationUpdate,
    database: DatabaseDependency,
    _: PharmacyWriterDependency,
) -> MedicationResponse:
    return update_medication(
        database,
        medication_id,
        payload,
    )


@medication_router.post(
    "/{medication_id}/stock",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_medication_stock(
    medication_id: int,
    payload: StockMovementCreate,
    database: DatabaseDependency,
    _: PharmacyWriterDependency,
) -> InventoryMovementResponse:
    return register_stock_movement(
        database,
        medication_id,
        payload,
    )


@prescription_router.post(
    "",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_prescription(
    payload: PrescriptionCreate,
    database: DatabaseDependency,
    _: PrescriptionWriterDependency,
) -> PrescriptionResponse:
    return create_prescription(
        database,
        payload,
    )


@prescription_router.get(
    "",
    response_model=PrescriptionListResponse,
)
def list_registered_prescriptions(
    database: DatabaseDependency,
    _: PharmacyReaderDependency,
    patient_id: int | None = None,
    prescription_status: Annotated[
        str | None,
        Query(alias="status"),
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> PrescriptionListResponse:
    return read_prescriptions(
        database=database,
        patient_id=patient_id,
        prescription_status=prescription_status,
        page=page,
        page_size=page_size,
    )


@prescription_router.get(
    "/{prescription_id}",
    response_model=PrescriptionResponse,
)
def get_registered_prescription(
    prescription_id: int,
    database: DatabaseDependency,
    _: PharmacyReaderDependency,
) -> PrescriptionResponse:
    return read_prescription(
        database,
        prescription_id,
    )


@prescription_router.patch(
    "/{prescription_id}/dispense",
    response_model=PrescriptionResponse,
)
def dispense_registered_prescription(
    prescription_id: int,
    database: DatabaseDependency,
    _: PharmacyWriterDependency,
) -> PrescriptionResponse:
    return dispense_prescription(
        database,
        prescription_id,
    )


@prescription_router.patch(
    "/{prescription_id}/cancel",
    response_model=PrescriptionResponse,
)
def cancel_registered_prescription(
    prescription_id: int,
    payload: PrescriptionCancel,
    database: DatabaseDependency,
    _: PrescriptionWriterDependency,
) -> PrescriptionResponse:
    return cancel_prescription(
        database,
        prescription_id,
        payload,
    )
