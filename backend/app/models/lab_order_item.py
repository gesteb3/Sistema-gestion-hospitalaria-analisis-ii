from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.lab_order import LabOrder
    from app.models.lab_result import LabResult
    from app.models.lab_test_type import LabTestType


class LabOrderItem(Base):
    __tablename__ = "detalle_ordenes_laboratorio"

    detalle_orden_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    orden_laboratorio_id: Mapped[int] = mapped_column(
        ForeignKey(
            "ordenes_laboratorio.orden_laboratorio_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    tipo_examen_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tipos_examen_laboratorio.tipo_examen_id"
        ),
        nullable=False,
        index=True,
    )
    observaciones: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDIENTE",
    )
    fecha_procesamiento: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    orden: Mapped["LabOrder"] = relationship(
        back_populates="items",
    )
    tipo_examen: Mapped["LabTestType"] = relationship(
        back_populates="items_orden",
        lazy="joined",
    )
    resultado: Mapped["LabResult | None"] = relationship(
        back_populates="item_orden",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
