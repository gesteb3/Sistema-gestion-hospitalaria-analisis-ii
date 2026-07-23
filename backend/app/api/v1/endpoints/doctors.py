from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import (
    DatabaseDependency,
    DoctorReaderDependency,
    DoctorWriterDependency,
)
from app.schemas.doctor import (
    DoctorCreate,
    DoctorListResponse,
    DoctorMessageResponse,
    DoctorResponse,
    DoctorUpdate,
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
)
from app.services.doctor_service import (
    create_doctor,
    create_schedule,
    deactivate_doctor,
    deactivate_schedule,
    list_schedules,
    reactivate_doctor,
    read_doctor,
    read_doctors,
    update_doctor,
    update_schedule,
)


router = APIRouter(
    prefix="/doctors",
    tags=["Médicos"],
)


@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_doctor(
    payload: DoctorCreate,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> DoctorResponse:
    return create_doctor(
        database,
        payload,
    )


@router.get(
    "",
    response_model=DoctorListResponse,
)
def list_registered_doctors(
    database: DatabaseDependency,
    _: DoctorReaderDependency,
    search: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
        ),
    ] = None,
    specialty_id: int | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
    include_inactive: bool = False,
) -> DoctorListResponse:
    return read_doctors(
        database=database,
        search=search,
        specialty_id=specialty_id,
        page=page,
        page_size=page_size,
        include_inactive=include_inactive,
    )


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
)
def get_registered_doctor(
    doctor_id: int,
    database: DatabaseDependency,
    _: DoctorReaderDependency,
) -> DoctorResponse:
    return read_doctor(
        database,
        doctor_id,
    )


@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse,
)
def modify_doctor(
    doctor_id: int,
    payload: DoctorUpdate,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> DoctorResponse:
    return update_doctor(
        database,
        doctor_id,
        payload,
    )


@router.delete(
    "/{doctor_id}",
    response_model=DoctorMessageResponse,
)
def remove_doctor(
    doctor_id: int,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> DoctorMessageResponse:
    return DoctorMessageResponse(
        message=deactivate_doctor(
            database,
            doctor_id,
        )
    )


@router.patch(
    "/{doctor_id}/reactivate",
    response_model=DoctorResponse,
)
def restore_doctor(
    doctor_id: int,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> DoctorResponse:
    return reactivate_doctor(
        database,
        doctor_id,
    )


@router.get(
    "/{doctor_id}/schedules",
    response_model=list[ScheduleResponse],
)
def list_doctor_schedules(
    doctor_id: int,
    database: DatabaseDependency,
    _: DoctorReaderDependency,
) -> list[ScheduleResponse]:
    return list_schedules(
        database,
        doctor_id,
    )


@router.post(
    "/{doctor_id}/schedules",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_doctor_schedule(
    doctor_id: int,
    payload: ScheduleCreate,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> ScheduleResponse:
    return create_schedule(
        database,
        doctor_id,
        payload,
    )


@router.put(
    "/{doctor_id}/schedules/{schedule_id}",
    response_model=ScheduleResponse,
)
def modify_doctor_schedule(
    doctor_id: int,
    schedule_id: int,
    payload: ScheduleUpdate,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> ScheduleResponse:
    return update_schedule(
        database,
        doctor_id,
        schedule_id,
        payload,
    )


@router.delete(
    "/{doctor_id}/schedules/{schedule_id}",
    response_model=DoctorMessageResponse,
)
def remove_doctor_schedule(
    doctor_id: int,
    schedule_id: int,
    database: DatabaseDependency,
    _: DoctorWriterDependency,
) -> DoctorMessageResponse:
    return DoctorMessageResponse(
        message=deactivate_schedule(
            database,
            doctor_id,
            schedule_id,
        )
    )
