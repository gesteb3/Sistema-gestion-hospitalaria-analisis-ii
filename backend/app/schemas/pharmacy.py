from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from app.utils.pharmacy import MOVEMENT_TYPES


def clean_optional_text(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = " ".join(str(value).strip().split())
    return cleaned or None


class MedicationCreate(BaseModel):
    codigo: str = Field(min_length=2, max_length=30)
    nombre: str = Field(min_length=2, max_length=150)
    principio_activo: str | None = Field(
        default=None,
        max_length=150,
    )
    concentracion: str | None = Field(
        default=None,
        max_length=80,
    )
    presentacion: str = Field(
        min_length=2,
        max_length=100,
    )
    unidad: str = Field(
        min_length=1,
        max_length=30,
    )
    stock_actual: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=5, ge=0)
    precio_unitario: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
    )

    @field_validator(
        "codigo",
        "nombre",
        "presentacion",
        "unidad",
    )
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("codigo")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.upper()

    @field_validator(
        "principio_activo",
        "concentracion",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)


class MedicationUpdate(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    principio_activo: str | None = Field(
        default=None,
        max_length=150,
    )
    concentracion: str | None = Field(
        default=None,
        max_length=80,
    )
    presentacion: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    unidad: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )
    stock_minimo: int | None = Field(
        default=None,
        ge=0,
    )
    precio_unitario: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )

    @field_validator(
        "nombre",
        "presentacion",
        "unidad",
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
        "principio_activo",
        "concentracion",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)

    @model_validator(mode="after")
    def validate_not_empty(self) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )
        return self


class MedicationResponse(BaseModel):
    medicamento_id: int
    codigo: str
    nombre: str
    principio_activo: str | None
    concentracion: str | None
    presentacion: str
    unidad: str
    stock_actual: int
    stock_minimo: int
    stock_bajo: bool
    precio_unitario: Decimal
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class MedicationListResponse(BaseModel):
    items: list[MedicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class StockMovementCreate(BaseModel):
    tipo: str
    cantidad: int = Field(gt=0)
    motivo: str = Field(min_length=3, max_length=500)

    @field_validator("tipo")
    @classmethod
    def validate_type(cls, value: str) -> str:
        normalized = value.strip().upper()

        if normalized not in {"ENTRADA", "AJUSTE"}:
            raise ValueError(
                "El tipo debe ser ENTRADA o AJUSTE."
            )

        return normalized

    @field_validator("motivo")
    @classmethod
    def clean_reason(cls, value: str) -> str:
        return " ".join(value.strip().split())


class InventoryMovementResponse(BaseModel):
    movimiento_id: int
    medicamento_id: int
    medicamento_nombre: str
    receta_id: int | None
    tipo: str
    cantidad: int
    stock_anterior: int
    stock_nuevo: int
    motivo: str
    fecha_movimiento: datetime


class PrescriptionItemInput(BaseModel):
    medicamento_id: int = Field(gt=0)
    dosis: str = Field(min_length=1, max_length=100)
    via_administracion: str = Field(
        min_length=2,
        max_length=80,
    )
    frecuencia: str = Field(
        min_length=2,
        max_length=100,
    )
    duracion: str = Field(
        min_length=2,
        max_length=100,
    )
    cantidad: int = Field(gt=0, le=1000)
    indicaciones: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator(
        "dosis",
        "via_administracion",
        "frecuencia",
        "duracion",
    )
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("indicaciones", mode="before")
    @classmethod
    def clean_instructions(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)


class PrescriptionCreate(BaseModel):
    consulta_id: int = Field(gt=0)
    indicaciones_generales: str | None = Field(
        default=None,
        max_length=1500,
    )
    items: list[PrescriptionItemInput] = Field(
        min_length=1,
        max_length=20,
    )

    @field_validator(
        "indicaciones_generales",
        mode="before",
    )
    @classmethod
    def clean_general_instructions(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)

    @field_validator("items")
    @classmethod
    def validate_unique_medications(
        cls,
        value: list[PrescriptionItemInput],
    ) -> list[PrescriptionItemInput]:
        medication_ids = [
            item.medicamento_id
            for item in value
        ]

        if len(medication_ids) != len(set(medication_ids)):
            raise ValueError(
                "No puede repetir un medicamento en la receta."
            )

        return value


class PrescriptionCancel(BaseModel):
    motivo_anulacion: str = Field(
        min_length=3,
        max_length=500,
    )

    @field_validator("motivo_anulacion")
    @classmethod
    def clean_reason(cls, value: str) -> str:
        return " ".join(value.strip().split())


class PrescriptionItemResponse(BaseModel):
    detalle_receta_id: int
    medicamento_id: int
    medicamento_codigo: str
    medicamento_nombre: str
    dosis: str
    via_administracion: str
    frecuencia: str
    duracion: str
    cantidad: int
    cantidad_dispensada: int
    indicaciones: str | None


class PrescriptionResponse(BaseModel):
    receta_id: int
    consulta_id: int
    paciente_id: int
    numero_expediente: str
    paciente_nombre: str
    medico_id: int
    medico_nombre: str
    indicaciones_generales: str | None
    estado: str
    motivo_anulacion: str | None
    items: list[PrescriptionItemResponse]
    fecha_emision: datetime
    fecha_dispensacion: datetime | None


class PrescriptionListResponse(BaseModel):
    items: list[PrescriptionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
