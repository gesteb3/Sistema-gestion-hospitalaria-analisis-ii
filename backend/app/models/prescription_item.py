from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Identity,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.medication import Medication
    from app.models.prescription import Prescription


class PrescriptionItem(Base):
    __tablename__ = "detalle_recetas"

    detalle_receta_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    receta_id: Mapped[int] = mapped_column(
        ForeignKey(
            "recetas.receta_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    medicamento_id: Mapped[int] = mapped_column(
        ForeignKey("medicamentos.medicamento_id"),
        nullable=False,
        index=True,
    )
    dosis: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    via_administracion: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    frecuencia: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    duracion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    cantidad_dispensada: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    indicaciones: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    receta: Mapped["Prescription"] = relationship(
        back_populates="items",
    )
    medicamento: Mapped["Medication"] = relationship(
        back_populates="items_receta",
        lazy="joined",
    )
