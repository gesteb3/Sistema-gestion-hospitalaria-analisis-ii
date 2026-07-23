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
    from app.models.invoice import Invoice


class Payment(Base):
    __tablename__ = "pagos"

    pago_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    factura_id: Mapped[int] = mapped_column(
        ForeignKey(
            "facturas.factura_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    monto: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    metodo_pago: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    referencia: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    observaciones: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="APLICADO",
    )
    fecha_pago: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    factura: Mapped["Invoice"] = relationship(
        back_populates="pagos",
    )
