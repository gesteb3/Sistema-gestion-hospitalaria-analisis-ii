import math

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.legal_guardian import LegalGuardian
from app.models.patient import Patient
from app.repositories.patient_repository import (
    get_patient_by_id,
    get_patient_by_identification,
    list_patients,
)
from app.schemas.patient import (
    LegalGuardianInput,
    LegalGuardianResponse,
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.utils.dates import (
    build_record_number,
    calculate_age,
    is_minor,
)


def patient_to_response(
    patient: Patient,
) -> PatientResponse:
    return PatientResponse(
        paciente_id=patient.paciente_id,
        numero_expediente=patient.numero_expediente or "",
        nombres=patient.nombres,
        apellidos=patient.apellidos,
        fecha_nacimiento=patient.fecha_nacimiento,
        edad=calculate_age(patient.fecha_nacimiento),
        menor_de_edad=is_minor(patient.fecha_nacimiento),
        sexo=patient.sexo,
        identificacion=patient.identificacion,
        telefono=patient.telefono,
        correo=patient.correo,
        direccion=patient.direccion,
        activo=patient.esta_activo,
        responsables_legales=[
            LegalGuardianResponse(
                responsable_id=guardian.responsable_id,
                nombres=guardian.nombres,
                apellidos=guardian.apellidos,
                identificacion=guardian.identificacion,
                parentesco=guardian.parentesco,
                telefono=guardian.telefono,
                correo=guardian.correo,
                principal=guardian.principal,
            )
            for guardian in patient.responsables_legales
        ],
        fecha_creacion=patient.fecha_creacion,
        fecha_actualizacion=patient.fecha_actualizacion,
    )


def build_guardian(
    payload: LegalGuardianInput,
) -> LegalGuardian:
    return LegalGuardian(
        nombres=payload.nombres,
        apellidos=payload.apellidos,
        identificacion=payload.identificacion,
        parentesco=payload.parentesco,
        telefono=payload.telefono,
        correo=(
            str(payload.correo).lower()
            if payload.correo is not None
            else None
        ),
        es_principal=1,
    )


def verify_unique_identification(
    database: Session,
    identification: str | None,
    current_patient_id: int | None = None,
) -> None:
    if identification is None:
        return

    existing = get_patient_by_identification(
        database,
        identification,
    )

    if (
        existing is not None
        and existing.paciente_id != current_patient_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La identificación del paciente ya está registrada.",
        )


def create_patient(
    database: Session,
    payload: PatientCreate,
) -> PatientResponse:
    verify_unique_identification(
        database,
        payload.identificacion,
    )

    if (
        is_minor(payload.fecha_nacimiento)
        and payload.responsable_legal is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Los pacientes menores de edad deben tener "
                "un responsable legal."
            ),
        )

    patient = Patient(
        nombres=payload.nombres,
        apellidos=payload.apellidos,
        fecha_nacimiento=payload.fecha_nacimiento,
        sexo=payload.sexo,
        identificacion=payload.identificacion,
        telefono=payload.telefono,
        correo=(
            str(payload.correo).lower()
            if payload.correo is not None
            else None
        ),
        direccion=payload.direccion,
        estado=1,
    )

    if payload.responsable_legal is not None:
        patient.responsables_legales.append(
            build_guardian(payload.responsable_legal)
        )

    try:
        database.add(patient)
        database.flush()

        patient.numero_expediente = build_record_number(
            patient.paciente_id
        )

        database.commit()
        database.refresh(patient)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No fue posible registrar el paciente porque "
                "existe información duplicada."
            ),
        ) from exc

    stored = get_patient_by_id(
        database,
        patient.paciente_id,
    )

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El paciente fue creado, pero no pudo recuperarse.",
        )

    return patient_to_response(stored)


def get_patient_or_404(
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

    return patient


def read_patient(
    database: Session,
    patient_id: int,
) -> PatientResponse:
    return patient_to_response(
        get_patient_or_404(database, patient_id)
    )


def read_patients(
    database: Session,
    search: str | None,
    page: int,
    page_size: int,
    include_inactive: bool,
) -> PatientListResponse:
    patients, total = list_patients(
        database=database,
        search=search,
        page=page,
        page_size=page_size,
        include_inactive=include_inactive,
    )

    total_pages = (
        math.ceil(total / page_size)
        if total > 0
        else 0
    )

    return PatientListResponse(
        items=[
            patient_to_response(patient)
            for patient in patients
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def update_guardian(
    patient: Patient,
    payload: LegalGuardianInput,
) -> None:
    if patient.responsables_legales:
        guardian = patient.responsables_legales[0]
        guardian.nombres = payload.nombres
        guardian.apellidos = payload.apellidos
        guardian.identificacion = payload.identificacion
        guardian.parentesco = payload.parentesco
        guardian.telefono = payload.telefono
        guardian.correo = (
            str(payload.correo).lower()
            if payload.correo is not None
            else None
        )
        guardian.es_principal = 1
        return

    patient.responsables_legales.append(
        build_guardian(payload)
    )


def update_patient(
    database: Session,
    patient_id: int,
    payload: PatientUpdate,
) -> PatientResponse:
    patient = get_patient_or_404(
        database,
        patient_id,
    )

    data = payload.model_dump(
        exclude_unset=True,
        exclude={"responsable_legal"},
    )

    if "identificacion" in data:
        verify_unique_identification(
            database,
            data["identificacion"],
            current_patient_id=patient_id,
        )

    if "correo" in data and data["correo"] is not None:
        data["correo"] = str(data["correo"]).lower()

    for field, value in data.items():
        setattr(patient, field, value)

    guardian_was_sent = (
        "responsable_legal" in payload.model_fields_set
        and payload.responsable_legal is not None
    )

    if guardian_was_sent:
        update_guardian(
            patient,
            payload.responsable_legal,
        )

    if (
        is_minor(patient.fecha_nacimiento)
        and not patient.responsables_legales
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Los pacientes menores de edad deben tener "
                "un responsable legal."
            ),
        )

    try:
        database.commit()
        database.refresh(patient)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No fue posible actualizar el paciente porque "
                "existe información duplicada."
            ),
        ) from exc

    updated = get_patient_by_id(
        database,
        patient_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible recuperar el paciente actualizado.",
        )

    return patient_to_response(updated)


def deactivate_patient(
    database: Session,
    patient_id: int,
) -> str:
    patient = get_patient_or_404(
        database,
        patient_id,
    )

    if not patient.esta_activo:
        return "El paciente ya se encontraba inactivo."

    patient.estado = 0
    database.commit()

    return "Paciente desactivado correctamente."


def reactivate_patient(
    database: Session,
    patient_id: int,
) -> PatientResponse:
    patient = get_patient_or_404(
        database,
        patient_id,
    )

    patient.estado = 1
    database.commit()
    database.refresh(patient)

    return patient_to_response(patient)
