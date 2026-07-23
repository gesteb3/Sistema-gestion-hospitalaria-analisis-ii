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
    from app.models.consultation import Consultation
    from app.models.inventory_movement import InventoryMovement
    from app.models.prescription_item import PrescriptionItem


class Prescription(Base):
    __tablename__ = "recetas"

    receta_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    consulta_id: Mapped[int] = mapped_column(
        ForeignKey(
            "consultas.consulta_id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )
    indicaciones_generales: Mapped[str | None] = mapped_column(
        String(1500),
        nullable=True,
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="EMITIDA",
        index=True,
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
    fecha_dispensacion: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    consulta: Mapped["Consultation"] = relationship(
        back_populates="receta",
        lazy="joined",
    )
    items: Mapped[list["PrescriptionItem"]] = relationship(
        back_populates="receta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    movimientos: Mapped[list["InventoryMovement"]] = relationship(
        back_populates="receta",
        lazy="selectin",
    )
