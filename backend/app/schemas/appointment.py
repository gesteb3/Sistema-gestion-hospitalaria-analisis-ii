from datetime import date, datetime
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from app.utils.appointments import (
    ALLOWED_APPOINTMENT_STATUSES,
    appointment_end_time,
)
from app.utils.schedules import validate_time_format


class AppointmentCreate(BaseModel):
    paciente_id: int = Field(gt=0)
    medico_id: int = Field(gt=0)
    fecha: date
    hora: str
    motivo: str = Field(min_length=3, max_length=500)
    observaciones: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("fecha")
    @classmethod
    def validate_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError(
                "No se puede programar una cita en una fecha pasada."
            )
        return value

    @field_validator("hora")
    @classmethod
    def validate_time(cls, value: str) -> str:
        return validate_time_format(value)

    @field_validator("motivo")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("observaciones", mode="before")
    @classmethod
    def normalize_observations(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None


class AppointmentUpdate(BaseModel):
    medico_id: int | None = Field(
        default=None,
        gt=0,
    )
    fecha: date | None = None
    hora: str | None = None
    motivo: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )
    observaciones: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("fecha")
    @classmethod
    def validate_optional_date(
        cls,
        value: date | None,
    ) -> date | None:
        if value is not None and value < date.today():
            raise ValueError(
                "No se puede reprogramar una cita "
                "en una fecha pasada."
            )
        return value

    @field_validator("hora")
    @classmethod
    def validate_optional_time(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        return validate_time_format(value)

    @field_validator("motivo")
    @classmethod
    def normalize_optional_reason(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        return " ".join(value.strip().split())

    @field_validator("observaciones", mode="before")
    @classmethod
    def normalize_optional_observations(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @model_validator(mode="after")
    def validate_not_empty(self) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )
        return self


class AppointmentStatusUpdate(BaseModel):
    estado: str
    motivo_cancelacion: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("estado")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().upper()

        if normalized not in ALLOWED_APPOINTMENT_STATUSES:
            allowed = ", ".join(
                sorted(ALLOWED_APPOINTMENT_STATUSES)
            )
            raise ValueError(
                f"El estado debe ser uno de estos valores: {allowed}."
            )

        return normalized

    @field_validator("motivo_cancelacion", mode="before")
    @classmethod
    def normalize_cancellation_reason(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @model_validator(mode="after")
    def validate_cancellation_reason(self) -> Self:
        if (
            self.estado == "CANCELADA"
            and not self.motivo_cancelacion
        ):
            raise ValueError(
                "Debe indicar el motivo de cancelación."
            )
        return self


class AppointmentResponse(BaseModel):
    cita_id: int
    paciente_id: int
    numero_expediente: str
    paciente_nombre: str
    medico_id: int
    medico_nombre: str
    numero_colegiado: str
    especialidades: list[str]
    fecha: date
    hora: str
    hora_fin: str
    duracion_minutos: int
    motivo: str
    observaciones: str | None
    estado: str
    motivo_cancelacion: str | None
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AvailabilitySlot(BaseModel):
    hora: str
    hora_fin: str
    duracion_minutos: int


class AppointmentAvailabilityResponse(BaseModel):
    medico_id: int
    medico_nombre: str
    fecha: date
    nombre_dia: str
    horarios_configurados: bool
    espacios_disponibles: list[AvailabilitySlot]


class AppointmentMessageResponse(BaseModel):
    message: str


def build_end_time(
    start_time: str,
    duration: int,
) -> str:
    return appointment_end_time(
        start_time,
        duration,
    )
