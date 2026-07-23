from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.medication import Medication
    from app.models.prescription import Prescription


class InventoryMovement(Base):
    __tablename__ = "movimientos_inventario"

    movimiento_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    medicamento_id: Mapped[int] = mapped_column(
        ForeignKey("medicamentos.medicamento_id"),
        nullable=False,
        index=True,
    )
    receta_id: Mapped[int | None] = mapped_column(
        ForeignKey("recetas.receta_id"),
        nullable=True,
        index=True,
    )
    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    stock_anterior: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    stock_nuevo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    motivo: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    fecha_movimiento: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    medicamento: Mapped["Medication"] = relationship(
        back_populates="movimientos",
        lazy="joined",
    )
    receta: Mapped["Prescription | None"] = relationship(
        back_populates="movimientos",
    )
