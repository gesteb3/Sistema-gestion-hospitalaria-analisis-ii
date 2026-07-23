from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.appointment import Appointment
from app.models.clinical_history import ClinicalHistory
from app.models.consultation import Consultation
from app.models.doctor import Doctor


CONSULTATION_LOAD_OPTIONS = (
    joinedload(Consultation.cita).joinedload(
        Appointment.paciente
    ),
    joinedload(Consultation.medico).selectinload(
        Doctor.especialidades
    ),
    selectinload(Consultation.signos_vitales),
    selectinload(Consultation.diagnosticos),
    selectinload(Consultation.tratamientos),
)


def get_history_by_patient_id(
    database: Session,
    patient_id: int,
) -> ClinicalHistory | None:
    statement = (
        select(ClinicalHistory)
        .options(
            joinedload(ClinicalHistory.paciente),
            selectinload(
                ClinicalHistory.consultas
            ).selectinload(Consultation.diagnosticos),
            selectinload(
                ClinicalHistory.consultas
            ).joinedload(Consultation.medico),
        )
        .where(
            ClinicalHistory.paciente_id == patient_id
        )
    )
    return database.scalar(statement)


def get_consultation_by_id(
    database: Session,
    consultation_id: int,
) -> Consultation | None:
    statement = (
        select(Consultation)
        .options(*CONSULTATION_LOAD_OPTIONS)
        .where(
            Consultation.consulta_id == consultation_id
        )
    )
    return database.scalar(statement)


def get_consultation_by_appointment_id(
    database: Session,
    appointment_id: int,
) -> Consultation | None:
    statement = (
        select(Consultation)
        .options(*CONSULTATION_LOAD_OPTIONS)
        .where(
            Consultation.cita_id == appointment_id
        )
    )
    return database.scalar(statement)


def list_consultations(
    database: Session,
    patient_id: int | None,
    doctor_id: int | None,
    page: int,
    page_size: int,
) -> tuple[list[Consultation], int]:
    filters = []

    if patient_id is not None:
        filters.append(
            Appointment.paciente_id == patient_id
        )

    if doctor_id is not None:
        filters.append(
            Consultation.medico_id == doctor_id
        )

    count_statement = (
        select(func.count(Consultation.consulta_id))
        .join(Consultation.cita)
    )
    statement = (
        select(Consultation)
        .join(Consultation.cita)
        .options(*CONSULTATION_LOAD_OPTIONS)
        .order_by(
            Consultation.fecha_atencion.desc(),
            Consultation.consulta_id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if filters:
        count_statement = count_statement.where(*filters)
        statement = statement.where(*filters)

    total = int(database.scalar(count_statement) or 0)
    consultations = list(
        database.scalars(statement).unique().all()
    )

    return consultations, total
