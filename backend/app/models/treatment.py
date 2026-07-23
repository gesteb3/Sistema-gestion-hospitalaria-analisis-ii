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


class Treatment(Base):
    __tablename__ = "tratamientos"

    tratamiento_id: Mapped[int] = mapped_column(
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
    descripcion: Mapped[str] = mapped_column(
        String(1500),
        nullable=False,
    )
    duracion: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    indicaciones: Mapped[str | None] = mapped_column(
        String(1500),
        nullable=True,
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVO",
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    consulta: Mapped["Consultation"] = relationship(
        back_populates="tratamientos",
    )
