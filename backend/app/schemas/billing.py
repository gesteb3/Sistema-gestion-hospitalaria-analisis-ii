from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from app.utils.billing import PAYMENT_METHODS


def clean_optional_text(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = " ".join(str(value).strip().split())
    return cleaned or None


class InvoiceItemInput(BaseModel):
    tipo_servicio: str = Field(
        min_length=2,
        max_length=30,
    )
    descripcion: str = Field(
        min_length=3,
        max_length=500,
    )
    cantidad: int = Field(gt=0, le=1000)
    precio_unitario: Decimal = Field(
        gt=0,
        decimal_places=2,
    )

    @field_validator(
        "tipo_servicio",
        "descripcion",
    )
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("tipo_servicio")
    @classmethod
    def normalize_service_type(
        cls,
        value: str,
    ) -> str:
        return value.upper()


class InvoiceCreate(BaseModel):
    paciente_id: int = Field(gt=0)
    consulta_id: int | None = Field(
        default=None,
        gt=0,
    )
    nit: str = Field(
        default="CF",
        min_length=2,
        max_length=20,
    )
    nombre_facturacion: str = Field(
        min_length=2,
        max_length=200,
    )
    direccion_facturacion: str | None = Field(
        default=None,
        max_length=300,
    )
    descuento: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
    )
    observaciones: str | None = Field(
        default=None,
        max_length=1000,
    )
    items: list[InvoiceItemInput] = Field(
        min_length=1,
        max_length=30,
    )

    @field_validator(
        "nit",
        "nombre_facturacion",
    )
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("nit")
    @classmethod
    def normalize_nit(cls, value: str) -> str:
        return value.upper()

    @field_validator(
        "direccion_facturacion",
        "observaciones",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)


class InvoiceUpdate(BaseModel):
    nit: str | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )
    nombre_facturacion: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )
    direccion_facturacion: str | None = Field(
        default=None,
        max_length=300,
    )
    observaciones: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator(
        "nit",
        "nombre_facturacion",
    )
    @classmethod
    def clean_optional_required(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        return " ".join(value.strip().split())

    @field_validator("nit")
    @classmethod
    def normalize_optional_nit(
        cls,
        value: str | None,
    ) -> str | None:
        return value.upper() if value is not None else None

    @field_validator(
        "direccion_facturacion",
        "observaciones",
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


class InvoiceCancel(BaseModel):
    motivo_anulacion: str = Field(
        min_length=3,
        max_length=500,
    )

    @field_validator("motivo_anulacion")
    @classmethod
    def clean_reason(cls, value: str) -> str:
        return " ".join(value.strip().split())


class PaymentCreate(BaseModel):
    monto: Decimal = Field(
        gt=0,
        decimal_places=2,
    )
    metodo_pago: str
    referencia: str | None = Field(
        default=None,
        max_length=100,
    )
    observaciones: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("metodo_pago")
    @classmethod
    def validate_method(cls, value: str) -> str:
        normalized = value.strip().upper()

        if normalized not in PAYMENT_METHODS:
            allowed = ", ".join(
                sorted(PAYMENT_METHODS)
            )
            raise ValueError(
                f"Método de pago no válido. Valores: {allowed}."
            )

        return normalized

    @field_validator(
        "referencia",
        "observaciones",
        mode="before",
    )
    @classmethod
    def clean_optional_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return clean_optional_text(value)


class InvoiceItemResponse(BaseModel):
    detalle_factura_id: int
    tipo_servicio: str
    descripcion: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class PaymentResponse(BaseModel):
    pago_id: int
    monto: Decimal
    metodo_pago: str
    referencia: str | None
    observaciones: str | None
    estado: str
    fecha_pago: datetime


class InvoiceResponse(BaseModel):
    factura_id: int
    numero_factura: str
    paciente_id: int
    numero_expediente: str
    paciente_nombre: str
    consulta_id: int | None
    nit: str
    nombre_facturacion: str
    direccion_facturacion: str | None
    subtotal: Decimal
    descuento: Decimal
    total: Decimal
    total_pagado: Decimal
    saldo_pendiente: Decimal
    estado: str
    observaciones: str | None
    motivo_anulacion: str | None
    items: list[InvoiceItemResponse]
    pagos: list[PaymentResponse]
    fecha_emision: datetime
    fecha_actualizacion: datetime


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BillingSummaryResponse(BaseModel):
    total_facturado: Decimal
    total_pagado: Decimal
    saldo_pendiente: Decimal
    facturas_pendientes: int
    facturas_parciales: int
    facturas_pagadas: int
