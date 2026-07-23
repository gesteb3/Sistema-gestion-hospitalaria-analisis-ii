from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.consultation import Consultation
    from app.models.invoice_item import InvoiceItem
    from app.models.patient import Patient
    from app.models.payment import Payment


class Invoice(Base):
    __tablename__ = "facturas"

    factura_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    numero_factura: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True,
        index=True,
    )
    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("pacientes.paciente_id"),
        nullable=False,
        index=True,
    )
    consulta_id: Mapped[int | None] = mapped_column(
        ForeignKey("consultas.consulta_id"),
        nullable=True,
        index=True,
    )
    nit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="CF",
    )
    nombre_facturacion: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    direccion_facturacion: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )
    descuento: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )
    total_pagado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )
    saldo_pendiente: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDIENTE",
        index=True,
    )
    observaciones: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    motivo_anulacion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    fecha_emision: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    paciente: Mapped["Patient"] = relationship(
        lazy="joined",
    )
    consulta: Mapped["Consultation | None"] = relationship(
        lazy="joined",
    )
    items: Mapped[list["InvoiceItem"]] = relationship(
        back_populates="factura",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    pagos: Mapped[list["Payment"]] = relationship(
        back_populates="factura",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
