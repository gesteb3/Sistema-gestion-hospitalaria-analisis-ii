from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.consultation import Consultation
from app.models.medication import Medication
from app.models.prescription import Prescription
from app.models.prescription_item import PrescriptionItem


PRESCRIPTION_LOAD_OPTIONS = (
    joinedload(Prescription.consulta)
    .joinedload(Consultation.cita),
    joinedload(Prescription.consulta)
    .joinedload(Consultation.medico),
    selectinload(Prescription.items)
    .joinedload(PrescriptionItem.medicamento),
)


def get_medication_by_id(
    database: Session,
    medication_id: int,
) -> Medication | None:
    return database.get(Medication, medication_id)


def get_medication_by_code(
    database: Session,
    code: str,
) -> Medication | None:
    statement = select(Medication).where(
        func.lower(Medication.codigo)
        == code.strip().lower()
    )
    return database.scalar(statement)


def list_medications(
    database: Session,
    search: str | None,
    low_stock: bool | None,
    include_inactive: bool,
    page: int,
    page_size: int,
) -> tuple[list[Medication], int]:
    filters = []

    if not include_inactive:
        filters.append(Medication.estado == 1)

    if search:
        pattern = f"%{search.strip().lower()}%"
        filters.append(
            or_(
                func.lower(Medication.codigo).like(pattern),
                func.lower(Medication.nombre).like(pattern),
                func.lower(Medication.principio_activo).like(pattern),
            )
        )

    if low_stock is True:
        filters.append(
            Medication.stock_actual
            <= Medication.stock_minimo
        )

    count_statement = select(
        func.count(Medication.medicamento_id)
    )
    statement = (
        select(Medication)
        .order_by(Medication.nombre)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if filters:
        count_statement = count_statement.where(*filters)
        statement = statement.where(*filters)

    total = int(database.scalar(count_statement) or 0)
    medications = list(database.scalars(statement).all())

    return medications, total


def get_prescription_by_id(
    database: Session,
    prescription_id: int,
) -> Prescription | None:
    statement = (
        select(Prescription)
        .options(*PRESCRIPTION_LOAD_OPTIONS)
        .where(Prescription.receta_id == prescription_id)
    )
    return database.scalar(statement)


def get_prescription_by_consultation_id(
    database: Session,
    consultation_id: int,
) -> Prescription | None:
    statement = (
        select(Prescription)
        .options(*PRESCRIPTION_LOAD_OPTIONS)
        .where(
            Prescription.consulta_id == consultation_id
        )
    )
    return database.scalar(statement)


def list_prescriptions(
    database: Session,
    patient_id: int | None,
    prescription_status: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Prescription], int]:
    filters = []

    if patient_id is not None:
        filters.append(
            Prescription.consulta.has(
                Consultation.cita.has(
                    paciente_id=patient_id
                )
            )
        )

    if prescription_status is not None:
        filters.append(
            Prescription.estado == prescription_status
        )

    count_statement = select(
        func.count(Prescription.receta_id)
    )
    statement = (
        select(Prescription)
        .options(*PRESCRIPTION_LOAD_OPTIONS)
        .order_by(
            Prescription.fecha_emision.desc(),
            Prescription.receta_id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if filters:
        count_statement = count_statement.where(*filters)
        statement = statement.where(*filters)

    total = int(database.scalar(count_statement) or 0)
    prescriptions = list(
        database.scalars(statement).unique().all()
    )

    return prescriptions, total
