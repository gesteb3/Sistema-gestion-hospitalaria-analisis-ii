from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.invoice import Invoice


class InvoiceItem(Base):
    __tablename__ = "detalle_facturas"

    detalle_factura_id: Mapped[int] = mapped_column(
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
    tipo_servicio: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    descripcion: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    factura: Mapped["Invoice"] = relationship(
        back_populates="items",
    )
