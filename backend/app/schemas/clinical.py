from datetime import datetime
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)


DIAGNOSIS_TYPES = {
    "PRESUNTIVO",
    "DEFINITIVO",
    "DIFERENCIAL",
}

TREATMENT_STATUSES = {
    "ACTIVO",
    "FINALIZADO",
    "SUSPENDIDO",
}


def normalize_optional_text(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = " ".join(str(value).strip().split())
    return cleaned or None


class ClinicalHistoryUpdate(BaseModel):
    alergias: str | None = Field(
        default=None,
        max_length=1000,
    )
    antecedentes_personales: str | None = Field(
        default=None,
        max_length=2000,
    )
    antecedentes_familiares: str | None = Field(
        default=None,
        max_length=2000,
    )
    enfermedades_cronicas: str | None = Field(
        default=None,
        max_length=1000,
    )
    cirugias_previas: str | None = Field(
        default=None,
        max_length=1000,
    )
    observaciones_generales: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("*", mode="before")
    @classmethod
    def clean_text(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_not_empty(self) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )
        return self


class VitalSignsInput(BaseModel):
    temperatura_c: float | None = Field(
        default=None,
        ge=30,
        le=45,
    )
    presion_sistolica: int | None = Field(
        default=None,
        ge=50,
        le=260,
    )
    presion_diastolica: int | None = Field(
        default=None,
        ge=30,
        le=180,
    )
    frecuencia_cardiaca: int | None = Field(
        default=None,
        ge=20,
        le=250,
    )
    frecuencia_respiratoria: int | None = Field(
        default=None,
        ge=5,
        le=80,
    )
    saturacion_oxigeno: int | None = Field(
        default=None,
        ge=50,
        le=100,
    )
    peso_kg: float | None = Field(
        default=None,
        gt=0,
        le=500,
    )
    estatura_cm: float | None = Field(
        default=None,
        gt=20,
        le=250,
    )
    observaciones: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("observaciones", mode="before")
    @classmethod
    def clean_observations(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_content(self) -> Self:
        values = self.model_dump()

        if not any(
            value is not None
            for value in values.values()
        ):
            raise ValueError(
                "Debe registrar al menos un signo vital."
            )

        if (
            self.presion_sistolica is not None
            and self.presion_diastolica is not None
            and self.presion_sistolica
            <= self.presion_diastolica
        ):
            raise ValueError(
                "La presión sistólica debe ser mayor "
                "que la presión diastólica."
            )

        return self


class DiagnosisInput(BaseModel):
    codigo_cie10: str | None = Field(
        default=None,
        max_length=15,
    )
    descripcion: str = Field(
        min_length=3,
        max_length=1000,
    )
    tipo: str = "PRESUNTIVO"
    es_principal: bool = False

    @field_validator("codigo_cie10", mode="before")
    @classmethod
    def clean_code(
        cls,
        value: str | None,
    ) -> str | None:
        normalized = normalize_optional_text(value)
        return (
            normalized.upper()
            if normalized is not None
            else None
        )

    @field_validator("descripcion")
    @classmethod
    def clean_description(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("tipo")
    @classmethod
    def validate_type(cls, value: str) -> str:
        normalized = value.strip().upper()

        if normalized not in DIAGNOSIS_TYPES:
            allowed = ", ".join(
                sorted(DIAGNOSIS_TYPES)
            )
            raise ValueError(
                f"El tipo debe ser uno de estos valores: {allowed}."
            )

        return normalized


class TreatmentInput(BaseModel):
    descripcion: str = Field(
        min_length=3,
        max_length=1500,
    )
    duracion: str | None = Field(
        default=None,
        max_length=100,
    )
    indicaciones: str | None = Field(
        default=None,
        max_length=1500,
    )
    estado: str = "ACTIVO"

    @field_validator("descripcion")
    @classmethod
    def clean_description(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator(
        "duracion",
        "indicaciones",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_optional_text(value)

    @field_validator("estado")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().upper()

        if normalized not in TREATMENT_STATUSES:
            allowed = ", ".join(
                sorted(TREATMENT_STATUSES)
            )
            raise ValueError(
                f"El estado debe ser uno de estos valores: {allowed}."
            )

        return normalized


class ConsultationCreate(BaseModel):
    cita_id: int = Field(gt=0)
    medico_id: int = Field(gt=0)
    motivo_consulta: str = Field(
        min_length=3,
        max_length=500,
    )
    sintomas: str | None = Field(
        default=None,
        max_length=1500,
    )
    evaluacion_clinica: str = Field(
        min_length=5,
        max_length=3000,
    )
    indicaciones_generales: str | None = Field(
        default=None,
        max_length=2000,
    )
    notas_medicas: str | None = Field(
        default=None,
        max_length=2000,
    )
    signos_vitales: VitalSignsInput | None = None
    diagnosticos: list[DiagnosisInput] = Field(
        default_factory=list,
        max_length=10,
    )
    tratamientos: list[TreatmentInput] = Field(
        default_factory=list,
        max_length=10,
    )

    @field_validator(
        "motivo_consulta",
        "evaluacion_clinica",
    )
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator(
        "sintomas",
        "indicaciones_generales",
        "notas_medicas",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_optional_text(value)


class ConsultationUpdate(BaseModel):
    motivo_consulta: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )
    sintomas: str | None = Field(
        default=None,
        max_length=1500,
    )
    evaluacion_clinica: str | None = Field(
        default=None,
        min_length=5,
        max_length=3000,
    )
    indicaciones_generales: str | None = Field(
        default=None,
        max_length=2000,
    )
    notas_medicas: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator(
        "motivo_consulta",
        "evaluacion_clinica",
    )
    @classmethod
    def clean_optional_required_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        return " ".join(value.strip().split())

    @field_validator(
        "sintomas",
        "indicaciones_generales",
        "notas_medicas",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_not_empty(self) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )
        return self


class VitalSignsResponse(BaseModel):
    signo_vital_id: int
    temperatura_c: float | None
    presion_sistolica: int | None
    presion_diastolica: int | None
    presion_arterial: str | None
    frecuencia_cardiaca: int | None
    frecuencia_respiratoria: int | None
    saturacion_oxigeno: int | None
    peso_kg: float | None
    estatura_cm: float | None
    imc: float | None
    observaciones: str | None
    fecha_registro: datetime


class DiagnosisResponse(BaseModel):
    diagnostico_id: int
    codigo_cie10: str | None
    descripcion: str
    tipo: str
    principal: bool
    fecha_registro: datetime


class TreatmentResponse(BaseModel):
    tratamiento_id: int
    descripcion: str
    duracion: str | None
    indicaciones: str | None
    estado: str
    fecha_registro: datetime


class ConsultationSummaryResponse(BaseModel):
    consulta_id: int
    cita_id: int
    medico_id: int
    medico_nombre: str
    fecha_atencion: datetime
    motivo_consulta: str
    diagnostico_principal: str | None


class ConsultationResponse(BaseModel):
    consulta_id: int
    historial_id: int
    cita_id: int
    paciente_id: int
    numero_expediente: str
    paciente_nombre: str
    medico_id: int
    medico_nombre: str
    fecha_atencion: datetime
    motivo_consulta: str
    sintomas: str | None
    evaluacion_clinica: str
    indicaciones_generales: str | None
    notas_medicas: str | None
    signos_vitales: VitalSignsResponse | None
    diagnosticos: list[DiagnosisResponse]
    tratamientos: list[TreatmentResponse]
    fecha_actualizacion: datetime


class ConsultationListResponse(BaseModel):
    items: list[ConsultationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ClinicalHistoryResponse(BaseModel):
    historial_id: int
    paciente_id: int
    numero_expediente: str
    paciente_nombre: str
    alergias: str | None
    antecedentes_personales: str | None
    antecedentes_familiares: str | None
    enfermedades_cronicas: str | None
    cirugias_previas: str | None
    observaciones_generales: str | None
    consultas: list[ConsultationSummaryResponse]
    fecha_creacion: datetime
    fecha_actualizacion: datetime
