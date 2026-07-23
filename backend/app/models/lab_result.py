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
    from app.models.lab_order_item import LabOrderItem


class LabResult(Base):
    __tablename__ = "resultados_laboratorio"

    resultado_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    detalle_orden_id: Mapped[int] = mapped_column(
        ForeignKey(
            "detalle_ordenes_laboratorio.detalle_orden_id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )
    resultado: Mapped[str] = mapped_column(
        String(3000),
        nullable=False,
    )
    valores_referencia: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    interpretacion: Mapped[str | None] = mapped_column(
        String(1500),
        nullable=True,
    )
    archivo_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    fecha_resultado: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    item_orden: Mapped["LabOrderItem"] = relationship(
        back_populates="resultado",
    )
