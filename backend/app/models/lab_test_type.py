from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Identity,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.lab_order_item import LabOrderItem


class LabTestType(Base):
    __tablename__ = "tipos_examen_laboratorio"

    tipo_examen_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    codigo: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )
    descripcion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    muestra_requerida: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    tiempo_estimado_horas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=24,
    )
    precio: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )
    estado: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    items_orden: Mapped[list["LabOrderItem"]] = relationship(
        back_populates="tipo_examen",
        lazy="selectin",
    )

    @property
    def esta_activo(self) -> bool:
        return self.estado == 1
