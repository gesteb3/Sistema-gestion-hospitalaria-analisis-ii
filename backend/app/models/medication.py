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
    from app.models.inventory_movement import InventoryMovement
    from app.models.prescription_item import PrescriptionItem


class Medication(Base):
    __tablename__ = "medicamentos"

    medicamento_id: Mapped[int] = mapped_column(
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
    principio_activo: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    concentracion: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )
    presentacion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    unidad: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    stock_actual: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    stock_minimo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
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
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    items_receta: Mapped[list["PrescriptionItem"]] = relationship(
        back_populates="medicamento",
        lazy="selectin",
    )
    movimientos: Mapped[list["InventoryMovement"]] = relationship(
        back_populates="medicamento",
        lazy="selectin",
    )

    @property
    def esta_activo(self) -> bool:
        return self.estado == 1

    @property
    def stock_bajo(self) -> bool:
        return self.stock_actual <= self.stock_minimo
