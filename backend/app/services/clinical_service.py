import math

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.clinical_history import ClinicalHistory
from app.models.consultation import Consultation
from app.models.diagnosis import Diagnosis
from app.models.treatment import Treatment
from app.models.vital_signs import VitalSigns
from app.repositories.appointment_repository import (
    get_appointment_by_id,
)
from app.repositories.clinical_repository import (
    get_consultation_by_appointment_id,
    get_consultation_by_id,
    get_history_by_patient_id,
    list_consultations,
)
from app.repositories.doctor_repository import (
    get_doctor_by_id,
)
from app.repositories.patient_repository import (
    get_patient_by_id,
)
from app.schemas.clinical import (
    ClinicalHistoryResponse,
    ClinicalHistoryUpdate,
    ConsultationCreate,
    ConsultationListResponse,
    ConsultationResponse,
    ConsultationSummaryResponse,
    ConsultationUpdate,
    DiagnosisInput,
    DiagnosisResponse,
    TreatmentInput,
    TreatmentResponse,
    VitalSignsInput,
    VitalSignsResponse,
)
from app.utils.clinical import (
    blood_pressure_text,
    calculate_bmi,
)


def vital_signs_to_response(
    vital_signs: VitalSigns | None,
) -> VitalSignsResponse | None:
    if vital_signs is None:
        return None

    return VitalSignsResponse(
        signo_vital_id=vital_signs.signo_vital_id,
        temperatura_c=vital_signs.temperatura_c,
        presion_sistolica=vital_signs.presion_sistolica,
        presion_diastolica=vital_signs.presion_diastolica,
        presion_arterial=blood_pressure_text(
            vital_signs.presion_sistolica,
            vital_signs.presion_diastolica,
        ),
        frecuencia_cardiaca=(
            vital_signs.frecuencia_cardiaca
        ),
        frecuencia_respiratoria=(
            vital_signs.frecuencia_respiratoria
        ),
        saturacion_oxigeno=(
            vital_signs.saturacion_oxigeno
        ),
        peso_kg=vital_signs.peso_kg,
        estatura_cm=vital_signs.estatura_cm,
        imc=vital_signs.imc,
        observaciones=vital_signs.observaciones,
        fecha_registro=vital_signs.fecha_registro,
    )


def diagnosis_to_response(
    diagnosis: Diagnosis,
) -> DiagnosisResponse:
    return DiagnosisResponse(
        diagnostico_id=diagnosis.diagnostico_id,
        codigo_cie10=diagnosis.codigo_cie10,
        descripcion=diagnosis.descripcion,
        tipo=diagnosis.tipo,
        principal=diagnosis.principal,
        fecha_registro=diagnosis.fecha_registro,
    )


def treatment_to_response(
    treatment: Treatment,
) -> TreatmentResponse:
    return TreatmentResponse(
        tratamiento_id=treatment.tratamiento_id,
        descripcion=treatment.descripcion,
        duracion=treatment.duracion,
        indicaciones=treatment.indicaciones,
        estado=treatment.estado,
        fecha_registro=treatment.fecha_registro,
    )


def consultation_to_response(
    consultation: Consultation,
) -> ConsultationResponse:
    appointment = consultation.cita
    patient = appointment.paciente

    return ConsultationResponse(
        consulta_id=consultation.consulta_id,
        historial_id=consultation.historial_id,
        cita_id=consultation.cita_id,
        paciente_id=patient.paciente_id,
        numero_expediente=(
            patient.numero_expediente or ""
        ),
        paciente_nombre=(
            f"{patient.nombres} {patient.apellidos}"
        ),
        medico_id=consultation.medico_id,
        medico_nombre=(
            f"{consultation.medico.nombres} "
            f"{consultation.medico.apellidos}"
        ),
        fecha_atencion=consultation.fecha_atencion,
        motivo_consulta=consultation.motivo_consulta,
        sintomas=consultation.sintomas,
        evaluacion_clinica=(
            consultation.evaluacion_clinica
        ),
        indicaciones_generales=(
            consultation.indicaciones_generales
        ),
        notas_medicas=consultation.notas_medicas,
        signos_vitales=vital_signs_to_response(
            consultation.signos_vitales
        ),
        diagnosticos=[
            diagnosis_to_response(diagnosis)
            for diagnosis in sorted(
                consultation.diagnosticos,
                key=lambda item: (
                    not item.principal,
                    item.diagnostico_id,
                ),
            )
        ],
        tratamientos=[
            treatment_to_response(treatment)
            for treatment in sorted(
                consultation.tratamientos,
                key=lambda item: item.tratamiento_id,
            )
        ],
        fecha_actualizacion=(
            consultation.fecha_actualizacion
        ),
    )


def history_to_response(
    history: ClinicalHistory,
) -> ClinicalHistoryResponse:
    patient = history.paciente

    summaries = []
    for consultation in sorted(
        history.consultas,
        key=lambda item: item.fecha_atencion,
        reverse=True,
    ):
        principal = next(
            (
                diagnosis.descripcion
                for diagnosis in consultation.diagnosticos
                if diagnosis.principal
            ),
            None,
        )

        summaries.append(
            ConsultationSummaryResponse(
                consulta_id=consultation.consulta_id,
                cita_id=consultation.cita_id,
                medico_id=consultation.medico_id,
                medico_nombre=(
                    f"{consultation.medico.nombres} "
                    f"{consultation.medico.apellidos}"
                ),
                fecha_atencion=(
                    consultation.fecha_atencion
                ),
                motivo_consulta=(
                    consultation.motivo_consulta
                ),
                diagnostico_principal=principal,
            )
        )

    return ClinicalHistoryResponse(
        historial_id=history.historial_id,
        paciente_id=patient.paciente_id,
        numero_expediente=(
            patient.numero_expediente or ""
        ),
        paciente_nombre=(
            f"{patient.nombres} {patient.apellidos}"
        ),
        alergias=history.alergias,
        antecedentes_personales=(
            history.antecedentes_personales
        ),
        antecedentes_familiares=(
            history.antecedentes_familiares
        ),
        enfermedades_cronicas=(
            history.enfermedades_cronicas
        ),
        cirugias_previas=history.cirugias_previas,
        observaciones_generales=(
            history.observaciones_generales
        ),
        consultas=summaries,
        fecha_creacion=history.fecha_creacion,
        fecha_actualizacion=history.fecha_actualizacion,
    )


def get_or_create_history(
    database: Session,
    patient_id: int,
) -> ClinicalHistory:
    history = get_history_by_patient_id(
        database,
        patient_id,
    )

    if history is not None:
        return history

    patient = get_patient_by_id(
        database,
        patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado.",
        )

    history = ClinicalHistory(
        paciente_id=patient_id,
    )
    database.add(history)
    database.flush()
    return history


def read_history(
    database: Session,
    patient_id: int,
) -> ClinicalHistoryResponse:
    patient = get_patient_by_id(
        database,
        patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado.",
        )

    history = get_history_by_patient_id(
        database,
        patient_id,
    )

    if history is None:
        history = ClinicalHistory(
            paciente_id=patient_id,
        )
        database.add(history)
        database.commit()

        history = get_history_by_patient_id(
            database,
            patient_id,
        )

    if history is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible crear el historial clínico."
            ),
        )

    return history_to_response(history)


def update_history(
    database: Session,
    patient_id: int,
    payload: ClinicalHistoryUpdate,
) -> ClinicalHistoryResponse:
    history = get_or_create_history(
        database,
        patient_id,
    )

    for field, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(history, field, value)

    database.commit()

    updated = get_history_by_patient_id(
        database,
        patient_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar el historial actualizado."
            ),
        )

    return history_to_response(updated)


def build_vital_signs(
    payload: VitalSignsInput,
) -> VitalSigns:
    return VitalSigns(
        temperatura_c=payload.temperatura_c,
        presion_sistolica=payload.presion_sistolica,
        presion_diastolica=payload.presion_diastolica,
        frecuencia_cardiaca=(
            payload.frecuencia_cardiaca
        ),
        frecuencia_respiratoria=(
            payload.frecuencia_respiratoria
        ),
        saturacion_oxigeno=(
            payload.saturacion_oxigeno
        ),
        peso_kg=payload.peso_kg,
        estatura_cm=payload.estatura_cm,
        imc=calculate_bmi(
            payload.peso_kg,
            payload.estatura_cm,
        ),
        observaciones=payload.observaciones,
    )


def build_diagnosis(
    payload: DiagnosisInput,
) -> Diagnosis:
    return Diagnosis(
        codigo_cie10=payload.codigo_cie10,
        descripcion=payload.descripcion,
        tipo=payload.tipo,
        es_principal=int(payload.es_principal),
    )


def build_treatment(
    payload: TreatmentInput,
) -> Treatment:
    return Treatment(
        descripcion=payload.descripcion,
        duracion=payload.duracion,
        indicaciones=payload.indicaciones,
        estado=payload.estado,
    )


def create_consultation(
    database: Session,
    payload: ConsultationCreate,
) -> ConsultationResponse:
    appointment = get_appointment_by_id(
        database,
        payload.cita_id,
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada.",
        )

    if appointment.estado in {
        "CANCELADA",
        "NO_ASISTIO",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede registrar una consulta para "
                "una cita cancelada o marcada como no asistida."
            ),
        )

    if appointment.medico_id != payload.medico_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El médico indicado no corresponde "
                "a la cita seleccionada."
            ),
        )

    if get_consultation_by_appointment_id(
        database,
        payload.cita_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "La cita ya tiene una consulta clínica registrada."
            ),
        )

    patient = get_patient_by_id(
        database,
        appointment.paciente_id,
    )
    doctor = get_doctor_by_id(
        database,
        payload.medico_id,
    )

    if patient is None or not patient.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El paciente no está disponible para atención.",
        )

    if doctor is None or not doctor.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El médico no está disponible para atención.",
        )

    history = get_or_create_history(
        database,
        appointment.paciente_id,
    )

    consultation = Consultation(
        historial_id=history.historial_id,
        cita_id=payload.cita_id,
        medico_id=payload.medico_id,
        motivo_consulta=payload.motivo_consulta,
        sintomas=payload.sintomas,
        evaluacion_clinica=(
            payload.evaluacion_clinica
        ),
        indicaciones_generales=(
            payload.indicaciones_generales
        ),
        notas_medicas=payload.notas_medicas,
    )

    if payload.signos_vitales is not None:
        consultation.signos_vitales = (
            build_vital_signs(
                payload.signos_vitales
            )
        )

    diagnoses = [
        build_diagnosis(diagnosis)
        for diagnosis in payload.diagnosticos
    ]

    principal_count = sum(
        diagnosis.es_principal
        for diagnosis in diagnoses
    )

    if principal_count > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Solo puede registrarse un diagnóstico principal."
            ),
        )

    consultation.diagnosticos.extend(diagnoses)
    consultation.tratamientos.extend(
        build_treatment(treatment)
        for treatment in payload.tratamientos
    )

    appointment.estado = "COMPLETADA"
    appointment.motivo_cancelacion = None
    database.add(consultation)

    try:
        database.commit()
        database.refresh(consultation)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No fue posible registrar la consulta clínica."
            ),
        ) from exc

    stored = get_consultation_by_id(
        database,
        consultation.consulta_id,
    )

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "La consulta fue creada, pero no pudo recuperarse."
            ),
        )

    return consultation_to_response(stored)


def get_consultation_or_404(
    database: Session,
    consultation_id: int,
) -> Consultation:
    consultation = get_consultation_by_id(
        database,
        consultation_id,
    )

    if consultation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta clínica no encontrada.",
        )

    return consultation


def read_consultation(
    database: Session,
    consultation_id: int,
) -> ConsultationResponse:
    return consultation_to_response(
        get_consultation_or_404(
            database,
            consultation_id,
        )
    )


def read_consultations(
    database: Session,
    patient_id: int | None,
    doctor_id: int | None,
    page: int,
    page_size: int,
) -> ConsultationListResponse:
    consultations, total = list_consultations(
        database=database,
        patient_id=patient_id,
        doctor_id=doctor_id,
        page=page,
        page_size=page_size,
    )

    return ConsultationListResponse(
        items=[
            consultation_to_response(consultation)
            for consultation in consultations
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


def update_consultation(
    database: Session,
    consultation_id: int,
    payload: ConsultationUpdate,
) -> ConsultationResponse:
    consultation = get_consultation_or_404(
        database,
        consultation_id,
    )

    for field, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(consultation, field, value)

    database.commit()

    updated = get_consultation_by_id(
        database,
        consultation_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar la consulta actualizada."
            ),
        )

    return consultation_to_response(updated)


def save_vital_signs(
    database: Session,
    consultation_id: int,
    payload: VitalSignsInput,
) -> ConsultationResponse:
    consultation = get_consultation_or_404(
        database,
        consultation_id,
    )

    if consultation.signos_vitales is None:
        consultation.signos_vitales = (
            build_vital_signs(payload)
        )
    else:
        vital_signs = consultation.signos_vitales
        values = payload.model_dump()

        for field, value in values.items():
            if field != "observaciones" and value is None:
                continue
            setattr(vital_signs, field, value)

        vital_signs.imc = calculate_bmi(
            vital_signs.peso_kg,
            vital_signs.estatura_cm,
        )

    database.commit()

    updated = get_consultation_by_id(
        database,
        consultation_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar los signos vitales."
            ),
        )

    return consultation_to_response(updated)


def add_diagnosis(
    database: Session,
    consultation_id: int,
    payload: DiagnosisInput,
) -> ConsultationResponse:
    consultation = get_consultation_or_404(
        database,
        consultation_id,
    )

    if payload.es_principal:
        for diagnosis in consultation.diagnosticos:
            diagnosis.es_principal = 0

    consultation.diagnosticos.append(
        build_diagnosis(payload)
    )
    database.commit()

    updated = get_consultation_by_id(
        database,
        consultation_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible recuperar el diagnóstico.",
        )

    return consultation_to_response(updated)


def add_treatment(
    database: Session,
    consultation_id: int,
    payload: TreatmentInput,
) -> ConsultationResponse:
    consultation = get_consultation_or_404(
        database,
        consultation_id,
    )
    consultation.tratamientos.append(
        build_treatment(payload)
    )
    database.commit()

    updated = get_consultation_by_id(
        database,
        consultation_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible recuperar el tratamiento.",
        )

    return consultation_to_response(updated)
