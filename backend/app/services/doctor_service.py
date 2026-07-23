import math

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from app.repositories.doctor_repository import (
    get_doctor_by_email,
    get_doctor_by_id,
    get_doctor_by_license,
    get_schedule_by_id,
    list_active_schedules_for_day,
    list_doctors,
)
from app.repositories.specialty_repository import (
    get_specialties_by_ids,
)
from app.schemas.doctor import (
    DoctorCreate,
    DoctorListResponse,
    DoctorResponse,
    DoctorUpdate,
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
    schedule_to_response,
)
from app.schemas.specialty import SpecialtyResponse
from app.utils.schedules import schedules_overlap


def doctor_to_response(
    doctor: Doctor,
) -> DoctorResponse:
    return DoctorResponse(
        medico_id=doctor.medico_id,
        nombres=doctor.nombres,
        apellidos=doctor.apellidos,
        nombre_completo=(
            f"{doctor.nombres} {doctor.apellidos}"
        ),
        numero_colegiado=doctor.numero_colegiado,
        telefono=doctor.telefono,
        correo=doctor.correo,
        direccion=doctor.direccion,
        activo=doctor.esta_activo,
        especialidades=[
            SpecialtyResponse(
                especialidad_id=specialty.especialidad_id,
                nombre=specialty.nombre,
                descripcion=specialty.descripcion,
                activa=specialty.esta_activa,
                fecha_creacion=specialty.fecha_creacion,
            )
            for specialty in doctor.especialidades
        ],
        horarios=[
            schedule_to_response(schedule)
            for schedule in sorted(
                (
                    item
                    for item in doctor.horarios
                    if item.esta_activo
                ),
                key=lambda item: (
                    item.dia_semana,
                    item.hora_inicio,
                ),
            )
        ],
        fecha_creacion=doctor.fecha_creacion,
        fecha_actualizacion=doctor.fecha_actualizacion,
    )


def get_doctor_or_404(
    database: Session,
    doctor_id: int,
) -> Doctor:
    doctor = get_doctor_by_id(
        database,
        doctor_id,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico no encontrado.",
        )

    return doctor


def validate_unique_doctor_data(
    database: Session,
    license_number: str | None,
    email: str | None,
    current_doctor_id: int | None = None,
) -> None:
    if license_number is not None:
        existing_license = get_doctor_by_license(
            database,
            license_number,
        )

        if (
            existing_license is not None
            and existing_license.medico_id
            != current_doctor_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El número de colegiado ya está registrado."
                ),
            )

    if email is not None:
        existing_email = get_doctor_by_email(
            database,
            email,
        )

        if (
            existing_email is not None
            and existing_email.medico_id
            != current_doctor_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo del médico ya está registrado.",
            )


def resolve_specialties(
    database: Session,
    specialty_ids: list[int],
):
    specialties = get_specialties_by_ids(
        database,
        specialty_ids,
    )

    found_ids = {
        specialty.especialidad_id
        for specialty in specialties
    }
    missing_ids = sorted(
        set(specialty_ids) - found_ids
    )

    if missing_ids:
        values = ", ".join(
            str(identifier)
            for identifier in missing_ids
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Especialidades inexistentes o inactivas: "
                f"{values}."
            ),
        )

    return specialties


def create_doctor(
    database: Session,
    payload: DoctorCreate,
) -> DoctorResponse:
    validate_unique_doctor_data(
        database,
        payload.numero_colegiado,
        str(payload.correo),
    )

    specialties = resolve_specialties(
        database,
        payload.especialidad_ids,
    )

    doctor = Doctor(
        nombres=payload.nombres,
        apellidos=payload.apellidos,
        numero_colegiado=payload.numero_colegiado,
        telefono=payload.telefono,
        correo=str(payload.correo).lower(),
        direccion=payload.direccion,
        estado=1,
        especialidades=specialties,
    )

    database.add(doctor)

    try:
        database.commit()
        database.refresh(doctor)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No fue posible registrar el médico porque "
                "existe información duplicada."
            ),
        ) from exc

    stored = get_doctor_by_id(
        database,
        doctor.medico_id,
    )

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El médico fue creado, pero no pudo recuperarse.",
        )

    return doctor_to_response(stored)


def read_doctors(
    database: Session,
    search: str | None,
    specialty_id: int | None,
    page: int,
    page_size: int,
    include_inactive: bool,
) -> DoctorListResponse:
    doctors, total = list_doctors(
        database=database,
        search=search,
        specialty_id=specialty_id,
        page=page,
        page_size=page_size,
        include_inactive=include_inactive,
    )

    return DoctorListResponse(
        items=[
            doctor_to_response(doctor)
            for doctor in doctors
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(
            math.ceil(total / page_size)
            if total > 0
            else 0
        ),
    )


def read_doctor(
    database: Session,
    doctor_id: int,
) -> DoctorResponse:
    return doctor_to_response(
        get_doctor_or_404(
            database,
            doctor_id,
        )
    )


def update_doctor(
    database: Session,
    doctor_id: int,
    payload: DoctorUpdate,
) -> DoctorResponse:
    doctor = get_doctor_or_404(
        database,
        doctor_id,
    )

    data = payload.model_dump(
        exclude_unset=True,
        exclude={"especialidad_ids"},
    )

    license_number = data.get("numero_colegiado")
    email = data.get("correo")

    validate_unique_doctor_data(
        database,
        license_number,
        str(email) if email is not None else None,
        current_doctor_id=doctor_id,
    )

    if email is not None:
        data["correo"] = str(email).lower()

    for field, value in data.items():
        setattr(doctor, field, value)

    if "especialidad_ids" in payload.model_fields_set:
        if payload.especialidad_ids is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Debe asignar al menos una especialidad."
                ),
            )

        doctor.especialidades = resolve_specialties(
            database,
            payload.especialidad_ids,
        )

    try:
        database.commit()
        database.refresh(doctor)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No fue posible actualizar el médico por "
                "información duplicada."
            ),
        ) from exc

    updated = get_doctor_by_id(
        database,
        doctor_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible recuperar el médico actualizado.",
        )

    return doctor_to_response(updated)


def deactivate_doctor(
    database: Session,
    doctor_id: int,
) -> str:
    doctor = get_doctor_or_404(
        database,
        doctor_id,
    )

    if not doctor.esta_activo:
        return "El médico ya se encontraba inactivo."

    doctor.estado = 0
    database.commit()

    return "Médico desactivado correctamente."


def reactivate_doctor(
    database: Session,
    doctor_id: int,
) -> DoctorResponse:
    doctor = get_doctor_or_404(
        database,
        doctor_id,
    )

    doctor.estado = 1
    database.commit()
    database.refresh(doctor)

    return doctor_to_response(doctor)


def validate_schedule_overlap(
    database: Session,
    doctor_id: int,
    day_number: int,
    start_time: str,
    end_time: str,
    exclude_schedule_id: int | None = None,
) -> None:
    schedules = list_active_schedules_for_day(
        database=database,
        doctor_id=doctor_id,
        day_number=day_number,
        exclude_schedule_id=exclude_schedule_id,
    )

    for schedule in schedules:
        if schedules_overlap(
            start_time,
            end_time,
            schedule.hora_inicio,
            schedule.hora_fin,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El horario se traslapa con otro horario "
                    "activo del médico."
                ),
            )


def create_schedule(
    database: Session,
    doctor_id: int,
    payload: ScheduleCreate,
) -> ScheduleResponse:
    doctor = get_doctor_or_404(
        database,
        doctor_id,
    )

    if not doctor.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se pueden asignar horarios a un médico inactivo."
            ),
        )

    validate_schedule_overlap(
        database=database,
        doctor_id=doctor_id,
        day_number=payload.dia_semana,
        start_time=payload.hora_inicio,
        end_time=payload.hora_fin,
    )

    schedule = DoctorSchedule(
        medico_id=doctor_id,
        dia_semana=payload.dia_semana,
        hora_inicio=payload.hora_inicio,
        hora_fin=payload.hora_fin,
        duracion_cita_minutos=(
            payload.duracion_cita_minutos
        ),
        estado=1,
    )

    database.add(schedule)
    database.commit()
    database.refresh(schedule)

    return schedule_to_response(schedule)


def list_schedules(
    database: Session,
    doctor_id: int,
) -> list[ScheduleResponse]:
    doctor = get_doctor_or_404(
        database,
        doctor_id,
    )

    return [
        schedule_to_response(schedule)
        for schedule in doctor.horarios
        if schedule.esta_activo
    ]


def update_schedule(
    database: Session,
    doctor_id: int,
    schedule_id: int,
    payload: ScheduleUpdate,
) -> ScheduleResponse:
    get_doctor_or_404(
        database,
        doctor_id,
    )

    schedule = get_schedule_by_id(
        database,
        schedule_id,
    )

    if (
        schedule is None
        or schedule.medico_id != doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horario médico no encontrado.",
        )

    data = payload.model_dump(exclude_unset=True)

    day_number = data.get(
        "dia_semana",
        schedule.dia_semana,
    )
    start_time = data.get(
        "hora_inicio",
        schedule.hora_inicio,
    )
    end_time = data.get(
        "hora_fin",
        schedule.hora_fin,
    )

    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "La hora de inicio debe ser menor "
                "que la hora final."
            ),
        )

    validate_schedule_overlap(
        database=database,
        doctor_id=doctor_id,
        day_number=day_number,
        start_time=start_time,
        end_time=end_time,
        exclude_schedule_id=schedule_id,
    )

    for field, value in data.items():
        setattr(schedule, field, value)

    database.commit()
    database.refresh(schedule)

    return schedule_to_response(schedule)


def deactivate_schedule(
    database: Session,
    doctor_id: int,
    schedule_id: int,
) -> str:
    get_doctor_or_404(
        database,
        doctor_id,
    )

    schedule = get_schedule_by_id(
        database,
        schedule_id,
    )

    if (
        schedule is None
        or schedule.medico_id != doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horario médico no encontrado.",
        )

    if not schedule.esta_activo:
        return "El horario ya se encontraba inactivo."

    schedule.estado = 0
    database.commit()

    return "Horario médico desactivado correctamente."
