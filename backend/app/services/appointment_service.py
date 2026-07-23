import math
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from app.models.patient import Patient
from app.repositories.appointment_repository import (
    get_appointment_by_id,
    list_active_appointments_for_doctor_date,
    list_active_appointments_for_patient_date,
    list_appointments,
)
from app.repositories.doctor_repository import (
    get_doctor_by_id,
    list_active_schedules_for_day,
)
from app.repositories.patient_repository import (
    get_patient_by_id,
)
from app.schemas.appointment import (
    AppointmentAvailabilityResponse,
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentStatusUpdate,
    AppointmentUpdate,
    AvailabilitySlot,
    build_end_time,
)
from app.utils.appointments import (
    ACTIVE_APPOINTMENT_STATUSES,
    FINAL_APPOINTMENT_STATUSES,
    appointment_day_number,
    appointment_overlaps,
    can_transition_status,
    generate_time_slots,
)
from app.utils.schedules import (
    day_name,
    time_to_minutes,
)


def appointment_to_response(
    appointment: Appointment,
) -> AppointmentResponse:
    return AppointmentResponse(
        cita_id=appointment.cita_id,
        paciente_id=appointment.paciente_id,
        numero_expediente=(
            appointment.paciente.numero_expediente or ""
        ),
        paciente_nombre=(
            f"{appointment.paciente.nombres} "
            f"{appointment.paciente.apellidos}"
        ),
        medico_id=appointment.medico_id,
        medico_nombre=(
            f"{appointment.medico.nombres} "
            f"{appointment.medico.apellidos}"
        ),
        numero_colegiado=(
            appointment.medico.numero_colegiado
        ),
        especialidades=sorted(
            specialty.nombre
            for specialty
            in appointment.medico.especialidades
            if specialty.esta_activa
        ),
        fecha=appointment.fecha,
        hora=appointment.hora,
        hora_fin=build_end_time(
            appointment.hora,
            appointment.duracion_minutos,
        ),
        duracion_minutos=appointment.duracion_minutos,
        motivo=appointment.motivo,
        observaciones=appointment.observaciones,
        estado=appointment.estado,
        motivo_cancelacion=(
            appointment.motivo_cancelacion
        ),
        fecha_creacion=appointment.fecha_creacion,
        fecha_actualizacion=(
            appointment.fecha_actualizacion
        ),
    )


def get_patient_for_appointment(
    database: Session,
    patient_id: int,
) -> Patient:
    patient = get_patient_by_id(
        database,
        patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado.",
        )

    if not patient.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede programar una cita "
                "para un paciente inactivo."
            ),
        )

    return patient


def get_doctor_for_appointment(
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

    if not doctor.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede programar una cita "
                "con un médico inactivo."
            ),
        )

    return doctor


def find_matching_schedule(
    database: Session,
    doctor_id: int,
    appointment_date: date,
    start_time: str,
) -> DoctorSchedule:
    day_number = appointment_day_number(
        appointment_date
    )
    schedules = list_active_schedules_for_day(
        database=database,
        doctor_id=doctor_id,
        day_number=day_number,
    )
    start_minutes = time_to_minutes(start_time)

    for schedule in schedules:
        schedule_start = time_to_minutes(
            schedule.hora_inicio
        )
        schedule_end = time_to_minutes(
            schedule.hora_fin
        )
        appointment_end = (
            start_minutes
            + schedule.duracion_cita_minutos
        )

        is_inside_schedule = (
            start_minutes >= schedule_start
            and appointment_end <= schedule_end
        )
        is_aligned = (
            start_minutes - schedule_start
        ) % schedule.duracion_cita_minutos == 0

        if is_inside_schedule and is_aligned:
            return schedule

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "La fecha y hora seleccionadas no corresponden "
            "a un horario disponible del médico."
        ),
    )


def validate_no_conflicts(
    database: Session,
    patient_id: int,
    doctor_id: int,
    appointment_date: date,
    start_time: str,
    duration_minutes: int,
    exclude_appointment_id: int | None = None,
) -> None:
    doctor_appointments = (
        list_active_appointments_for_doctor_date(
            database=database,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            exclude_appointment_id=(
                exclude_appointment_id
            ),
        )
    )

    for appointment in doctor_appointments:
        if appointment_overlaps(
            start_time,
            duration_minutes,
            appointment.hora,
            appointment.duracion_minutos,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El médico ya tiene una cita programada "
                    "en ese horario."
                ),
            )

    patient_appointments = (
        list_active_appointments_for_patient_date(
            database=database,
            patient_id=patient_id,
            appointment_date=appointment_date,
            exclude_appointment_id=(
                exclude_appointment_id
            ),
        )
    )

    for appointment in patient_appointments:
        if appointment_overlaps(
            start_time,
            duration_minutes,
            appointment.hora,
            appointment.duracion_minutos,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El paciente ya tiene una cita programada "
                    "en ese horario."
                ),
            )


def create_appointment(
    database: Session,
    payload: AppointmentCreate,
) -> AppointmentResponse:
    get_patient_for_appointment(
        database,
        payload.paciente_id,
    )
    get_doctor_for_appointment(
        database,
        payload.medico_id,
    )

    schedule = find_matching_schedule(
        database=database,
        doctor_id=payload.medico_id,
        appointment_date=payload.fecha,
        start_time=payload.hora,
    )

    validate_no_conflicts(
        database=database,
        patient_id=payload.paciente_id,
        doctor_id=payload.medico_id,
        appointment_date=payload.fecha,
        start_time=payload.hora,
        duration_minutes=(
            schedule.duracion_cita_minutos
        ),
    )

    appointment = Appointment(
        paciente_id=payload.paciente_id,
        medico_id=payload.medico_id,
        fecha=payload.fecha,
        hora=payload.hora,
        duracion_minutos=(
            schedule.duracion_cita_minutos
        ),
        motivo=payload.motivo,
        observaciones=payload.observaciones,
        estado="PROGRAMADA",
    )

    database.add(appointment)

    try:
        database.commit()
        database.refresh(appointment)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar la cita.",
        ) from exc

    stored = get_appointment_by_id(
        database,
        appointment.cita_id,
    )

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "La cita fue creada, pero no pudo recuperarse."
            ),
        )

    return appointment_to_response(stored)


def get_appointment_or_404(
    database: Session,
    appointment_id: int,
) -> Appointment:
    appointment = get_appointment_by_id(
        database,
        appointment_id,
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada.",
        )

    return appointment


def read_appointment(
    database: Session,
    appointment_id: int,
) -> AppointmentResponse:
    return appointment_to_response(
        get_appointment_or_404(
            database,
            appointment_id,
        )
    )


def read_appointments(
    database: Session,
    patient_id: int | None,
    doctor_id: int | None,
    appointment_status: str | None,
    date_from: date | None,
    date_to: date | None,
    page: int,
    page_size: int,
) -> AppointmentListResponse:
    if (
        date_from is not None
        and date_to is not None
        and date_from > date_to
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "La fecha inicial no puede ser mayor "
                "que la fecha final."
            ),
        )

    normalized_status = (
        appointment_status.strip().upper()
        if appointment_status is not None
        else None
    )

    appointments, total = list_appointments(
        database=database,
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_status=normalized_status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )

    return AppointmentListResponse(
        items=[
            appointment_to_response(appointment)
            for appointment in appointments
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


def update_appointment(
    database: Session,
    appointment_id: int,
    payload: AppointmentUpdate,
) -> AppointmentResponse:
    appointment = get_appointment_or_404(
        database,
        appointment_id,
    )

    if appointment.estado in FINAL_APPOINTMENT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede modificar una cita finalizada "
                "o cancelada."
            ),
        )

    doctor_id = (
        payload.medico_id
        if payload.medico_id is not None
        else appointment.medico_id
    )
    appointment_date = (
        payload.fecha
        if payload.fecha is not None
        else appointment.fecha
    )
    start_time = (
        payload.hora
        if payload.hora is not None
        else appointment.hora
    )

    get_doctor_for_appointment(
        database,
        doctor_id,
    )

    schedule = find_matching_schedule(
        database=database,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        start_time=start_time,
    )

    validate_no_conflicts(
        database=database,
        patient_id=appointment.paciente_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        start_time=start_time,
        duration_minutes=(
            schedule.duracion_cita_minutos
        ),
        exclude_appointment_id=appointment_id,
    )

    data = payload.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(appointment, field, value)

    appointment.duracion_minutos = (
        schedule.duracion_cita_minutos
    )

    database.commit()
    database.refresh(appointment)

    updated = get_appointment_by_id(
        database,
        appointment_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar la cita actualizada."
            ),
        )

    return appointment_to_response(updated)


def update_appointment_status(
    database: Session,
    appointment_id: int,
    payload: AppointmentStatusUpdate,
) -> AppointmentResponse:
    appointment = get_appointment_or_404(
        database,
        appointment_id,
    )

    if not can_transition_status(
        appointment.estado,
        payload.estado,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No se permite cambiar una cita de "
                f"{appointment.estado} a {payload.estado}."
            ),
        )

    appointment.estado = payload.estado
    appointment.motivo_cancelacion = (
        payload.motivo_cancelacion
        if payload.estado == "CANCELADA"
        else None
    )

    database.commit()
    database.refresh(appointment)

    updated = get_appointment_by_id(
        database,
        appointment_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar la cita actualizada."
            ),
        )

    return appointment_to_response(updated)


def cancel_appointment(
    database: Session,
    appointment_id: int,
    reason: str,
) -> AppointmentResponse:
    return update_appointment_status(
        database=database,
        appointment_id=appointment_id,
        payload=AppointmentStatusUpdate(
            estado="CANCELADA",
            motivo_cancelacion=reason,
        ),
    )


def read_availability(
    database: Session,
    doctor_id: int,
    appointment_date: date,
) -> AppointmentAvailabilityResponse:
    if appointment_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede consultar disponibilidad "
                "de una fecha pasada."
            ),
        )

    doctor = get_doctor_for_appointment(
        database,
        doctor_id,
    )
    day_number = appointment_day_number(
        appointment_date
    )
    schedules = list_active_schedules_for_day(
        database=database,
        doctor_id=doctor_id,
        day_number=day_number,
    )

    appointments = (
        list_active_appointments_for_doctor_date(
            database=database,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
        )
    )

    available_slots: list[AvailabilitySlot] = []

    for schedule in schedules:
        slots = generate_time_slots(
            schedule.hora_inicio,
            schedule.hora_fin,
            schedule.duracion_cita_minutos,
        )

        for slot in slots:
            occupied = any(
                appointment_overlaps(
                    slot,
                    schedule.duracion_cita_minutos,
                    appointment.hora,
                    appointment.duracion_minutos,
                )
                for appointment in appointments
            )

            if not occupied:
                available_slots.append(
                    AvailabilitySlot(
                        hora=slot,
                        hora_fin=build_end_time(
                            slot,
                            schedule.duracion_cita_minutos,
                        ),
                        duracion_minutos=(
                            schedule.duracion_cita_minutos
                        ),
                    )
                )

    available_slots.sort(key=lambda slot: slot.hora)

    return AppointmentAvailabilityResponse(
        medico_id=doctor.medico_id,
        medico_nombre=(
            f"{doctor.nombres} {doctor.apellidos}"
        ),
        fecha=appointment_date,
        nombre_dia=day_name(day_number),
        horarios_configurados=bool(schedules),
        espacios_disponibles=available_slots,
    )
