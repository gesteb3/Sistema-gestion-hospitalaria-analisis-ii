from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import (
    AppointmentReaderDependency,
    AppointmentStatusDependency,
    AppointmentWriterDependency,
    DatabaseDependency,
)
from app.schemas.appointment import (
    AppointmentAvailabilityResponse,
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentStatusUpdate,
    AppointmentUpdate,
)
from app.services.appointment_service import (
    create_appointment,
    read_appointment,
    read_appointments,
    read_availability,
    update_appointment,
    update_appointment_status,
)


router = APIRouter(
    prefix="/appointments",
    tags=["Citas"],
)


@router.get(
    "/availability",
    response_model=AppointmentAvailabilityResponse,
)
def get_doctor_availability(
    doctor_id: int,
    appointment_date: Annotated[
        date,
        Query(alias="date"),
    ],
    database: DatabaseDependency,
    _: AppointmentReaderDependency,
) -> AppointmentAvailabilityResponse:
    return read_availability(
        database=database,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
    )


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_appointment(
    payload: AppointmentCreate,
    database: DatabaseDependency,
    _: AppointmentWriterDependency,
) -> AppointmentResponse:
    return create_appointment(
        database,
        payload,
    )


@router.get(
    "",
    response_model=AppointmentListResponse,
)
def list_registered_appointments(
    database: DatabaseDependency,
    _: AppointmentReaderDependency,
    patient_id: int | None = None,
    doctor_id: int | None = None,
    appointment_status: Annotated[
        str | None,
        Query(alias="status"),
    ] = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> AppointmentListResponse:
    return read_appointments(
        database=database,
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_status=appointment_status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_registered_appointment(
    appointment_id: int,
    database: DatabaseDependency,
    _: AppointmentReaderDependency,
) -> AppointmentResponse:
    return read_appointment(
        database,
        appointment_id,
    )


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def reschedule_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    database: DatabaseDependency,
    _: AppointmentWriterDependency,
) -> AppointmentResponse:
    return update_appointment(
        database,
        appointment_id,
        payload,
    )


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
)
def change_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    database: DatabaseDependency,
    _: AppointmentStatusDependency,
) -> AppointmentResponse:
    return update_appointment_status(
        database,
        appointment_id,
        payload,
    )
