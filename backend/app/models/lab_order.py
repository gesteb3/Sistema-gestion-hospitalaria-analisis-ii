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
    from app.models.lab_order_item import LabOrderItem


class LabOrder(Base):
    __tablename__ = "ordenes_laboratorio"

    orden_laboratorio_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    consulta_id: Mapped[int] = mapped_column(
        ForeignKey(
            "consultas.consulta_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    indicaciones: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    prioridad: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NORMAL",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="SOLICITADA",
        index=True,
    )
    motivo_cancelacion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    fecha_completada: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    consulta: Mapped["Consultation"] = relationship(
        back_populates="ordenes_laboratorio",
        lazy="joined",
    )
    items: Mapped[list["LabOrderItem"]] = relationship(
        back_populates="orden",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
