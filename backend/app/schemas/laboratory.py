from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from app.utils.laboratory import (
    LAB_ORDER_STATUSES,
    LAB_PRIORITIES,
)


def clean_optional_text(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = " ".join(str(value).strip().split())
    return cleaned or None


class LabTestTypeCreate(BaseModel):
    codigo: str = Field(min_length=2, max_length=30)
    nombre: str = Field(min_length=3, max_length=150)
    descripcion: str | None = Field(
        default=None,
        max_length=500,
    )
    muestra_requerida: str = Field(
        min_length=2,
        max_length=100,
    )
    tiempo_estimado_horas: int = Field(
        default=24,
        ge=1,
        le=720,
    )
    precio: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
    )

    @field_validator(
        "codigo",
        "nombre",
        "muestra_requerida",
    )
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("codigo")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.upper()

    @field_validator("descripcion", mode="before")
    @classmethod
    def clean_description(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)


class LabTestTypeUpdate(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )
    descripcion: str | None = Field(
        default=None,
        max_length=500,
    )
    muestra_requerida: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    tiempo_estimado_horas: int | None = Field(
        default=None,
        ge=1,
        le=720,
    )
    precio: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )

    @field_validator(
        "nombre",
        "muestra_requerida",
    )
    @classmethod
    def clean_optional_required_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        return " ".join(value.strip().split())

    @field_validator("descripcion", mode="before")
    @classmethod
    def clean_description(
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


class LabTestTypeResponse(BaseModel):
    tipo_examen_id: int
    codigo: str
    nombre: str
    descripcion: str | None
    muestra_requerida: str
    tiempo_estimado_horas: int
    precio: Decimal
    activo: bool
    fecha_creacion: datetime


class LabOrderItemInput(BaseModel):
    tipo_examen_id: int = Field(gt=0)
    observaciones: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("observaciones", mode="before")
    @classmethod
    def clean_observations(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)


class LabOrderCreate(BaseModel):
    consulta_id: int = Field(gt=0)
    indicaciones: str | None = Field(
        default=None,
        max_length=1000,
    )
    prioridad: str = "NORMAL"
    items: list[LabOrderItemInput] = Field(
        min_length=1,
        max_length=20,
    )

    @field_validator("indicaciones", mode="before")
    @classmethod
    def clean_instructions(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)

    @field_validator("prioridad")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        normalized = value.strip().upper()

        if normalized not in LAB_PRIORITIES:
            raise ValueError(
                "La prioridad debe ser NORMAL o URGENTE."
            )

        return normalized

    @field_validator("items")
    @classmethod
    def validate_unique_tests(
        cls,
        value: list[LabOrderItemInput],
    ) -> list[LabOrderItemInput]:
        test_ids = [
            item.tipo_examen_id
            for item in value
        ]

        if len(test_ids) != len(set(test_ids)):
            raise ValueError(
                "No puede repetir un examen en la misma orden."
            )

        return value


class LabOrderStatusUpdate(BaseModel):
    estado: str
    motivo_cancelacion: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("estado")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().upper()

        if normalized not in LAB_ORDER_STATUSES:
            allowed = ", ".join(
                sorted(LAB_ORDER_STATUSES)
            )
            raise ValueError(
                f"Estado no válido. Valores: {allowed}."
            )

        return normalized

    @field_validator("motivo_cancelacion", mode="before")
    @classmethod
    def clean_reason(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)

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


class LabResultCreate(BaseModel):
    resultado: str = Field(
        min_length=2,
        max_length=3000,
    )
    valores_referencia: str | None = Field(
        default=None,
        max_length=1000,
    )
    interpretacion: str | None = Field(
        default=None,
        max_length=1500,
    )
    archivo_url: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("resultado")
    @classmethod
    def clean_result(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator(
        "valores_referencia",
        "interpretacion",
        "archivo_url",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)


class LabResultResponse(BaseModel):
    resultado_id: int
    resultado: str
    valores_referencia: str | None
    interpretacion: str | None
    archivo_url: str | None
    fecha_resultado: datetime


class LabOrderItemResponse(BaseModel):
    detalle_orden_id: int
    tipo_examen_id: int
    codigo_examen: str
    nombre_examen: str
    muestra_requerida: str
    precio: Decimal
    observaciones: str | None
    estado: str
    fecha_procesamiento: datetime | None
    resultado: LabResultResponse | None


class LabOrderResponse(BaseModel):
    orden_laboratorio_id: int
    consulta_id: int
    paciente_id: int
    numero_expediente: str
    paciente_nombre: str
    medico_id: int
    medico_nombre: str
    indicaciones: str | None
    prioridad: str
    estado: str
    motivo_cancelacion: str | None
    items: list[LabOrderItemResponse]
    total_estimado: Decimal
    fecha_solicitud: datetime
    fecha_completada: datetime | None


class LabOrderListResponse(BaseModel):
    items: list[LabOrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
