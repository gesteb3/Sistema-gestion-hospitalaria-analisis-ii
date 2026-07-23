from datetime import datetime
from typing import Self

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.schemas.specialty import SpecialtyResponse
from app.utils.schedules import (
    day_name,
    validate_time_format,
)


class ScheduleCreate(BaseModel):
    dia_semana: int = Field(ge=1, le=7)
    hora_inicio: str
    hora_fin: str
    duracion_cita_minutos: int = Field(
        default=30,
        ge=10,
        le=240,
    )

    @field_validator("hora_inicio", "hora_fin")
    @classmethod
    def validate_time(cls, value: str) -> str:
        return validate_time_format(value)

    @model_validator(mode="after")
    def validate_time_range(self) -> Self:
        if self.hora_inicio >= self.hora_fin:
            raise ValueError(
                "La hora de inicio debe ser menor que la hora final."
            )

        return self


class ScheduleUpdate(BaseModel):
    dia_semana: int | None = Field(
        default=None,
        ge=1,
        le=7,
    )
    hora_inicio: str | None = None
    hora_fin: str | None = None
    duracion_cita_minutos: int | None = Field(
        default=None,
        ge=10,
        le=240,
    )

    @field_validator("hora_inicio", "hora_fin")
    @classmethod
    def validate_optional_time(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return validate_time_format(value)

    @model_validator(mode="after")
    def validate_not_empty(self) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )

        return self


class ScheduleResponse(BaseModel):
    horario_id: int
    dia_semana: int
    nombre_dia: str
    hora_inicio: str
    hora_fin: str
    duracion_cita_minutos: int
    activo: bool


class DoctorCreate(BaseModel):
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    numero_colegiado: str = Field(
        min_length=3,
        max_length=30,
    )
    telefono: str | None = Field(
        default=None,
        min_length=8,
        max_length=20,
    )
    correo: EmailStr
    direccion: str | None = Field(
        default=None,
        max_length=250,
    )
    especialidad_ids: list[int] = Field(
        min_length=1,
    )

    @field_validator(
        "nombres",
        "apellidos",
        "numero_colegiado",
    )
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        return " ".join(value.strip().split())

    @field_validator("numero_colegiado")
    @classmethod
    def normalize_license(
        cls,
        value: str,
    ) -> str:
        return value.upper()

    @field_validator(
        "telefono",
        "direccion",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = str(value).strip()
        return cleaned or None

    @field_validator("especialidad_ids")
    @classmethod
    def normalize_specialties(
        cls,
        value: list[int],
    ) -> list[int]:
        normalized = sorted(set(value))

        if not normalized:
            raise ValueError(
                "Debe asignar al menos una especialidad."
            )

        return normalized


class DoctorUpdate(BaseModel):
    nombres: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    apellidos: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    numero_colegiado: str | None = Field(
        default=None,
        min_length=3,
        max_length=30,
    )
    telefono: str | None = Field(
        default=None,
        min_length=8,
        max_length=20,
    )
    correo: EmailStr | None = None
    direccion: str | None = Field(
        default=None,
        max_length=250,
    )
    especialidad_ids: list[int] | None = None

    @field_validator(
        "nombres",
        "apellidos",
        "numero_colegiado",
    )
    @classmethod
    def normalize_optional_required_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return " ".join(value.strip().split())

    @field_validator("numero_colegiado")
    @classmethod
    def normalize_optional_license(
        cls,
        value: str | None,
    ) -> str | None:
        return value.upper() if value is not None else None

    @field_validator(
        "telefono",
        "direccion",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = str(value).strip()
        return cleaned or None

    @field_validator("especialidad_ids")
    @classmethod
    def normalize_optional_specialties(
        cls,
        value: list[int] | None,
    ) -> list[int] | None:
        if value is None:
            return None

        normalized = sorted(set(value))

        if not normalized:
            raise ValueError(
                "Debe asignar al menos una especialidad."
            )

        return normalized

    @model_validator(mode="after")
    def validate_not_empty(self) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )

        return self


class DoctorResponse(BaseModel):
    medico_id: int
    nombres: str
    apellidos: str
    nombre_completo: str
    numero_colegiado: str
    telefono: str | None
    correo: EmailStr
    direccion: str | None
    activo: bool
    especialidades: list[SpecialtyResponse]
    horarios: list[ScheduleResponse]
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class DoctorListResponse(BaseModel):
    items: list[DoctorResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DoctorMessageResponse(BaseModel):
    message: str


def schedule_to_response(
    schedule,
) -> ScheduleResponse:
    return ScheduleResponse(
        horario_id=schedule.horario_id,
        dia_semana=schedule.dia_semana,
        nombre_dia=day_name(schedule.dia_semana),
        hora_inicio=schedule.hora_inicio,
        hora_fin=schedule.hora_fin,
        duracion_cita_minutos=schedule.duracion_cita_minutos,
        activo=schedule.esta_activo,
    )
