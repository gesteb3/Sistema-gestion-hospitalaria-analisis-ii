from datetime import datetime
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class SpecialtyCreate(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    descripcion: str | None = Field(
        default=None,
        max_length=300,
    )

    @field_validator("nombre")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("descripcion", mode="before")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = str(value).strip()
        return cleaned or None


class SpecialtyUpdate(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )
    descripcion: str | None = Field(
        default=None,
        max_length=300,
    )

    @field_validator("nombre")
    @classmethod
    def normalize_optional_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return " ".join(value.strip().split())

    @field_validator("descripcion", mode="before")
    @classmethod
    def normalize_optional_description(
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


class SpecialtyResponse(BaseModel):
    especialidad_id: int
    nombre: str
    descripcion: str | None
    activa: bool
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
