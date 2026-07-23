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
    from app.models.patient import Patient


class ClinicalHistory(Base):
    __tablename__ = "historiales_clinicos"

    historial_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    paciente_id: Mapped[int] = mapped_column(
        ForeignKey(
            "pacientes.paciente_id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )
    alergias: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    antecedentes_personales: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    antecedentes_familiares: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    enfermedades_cronicas: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    cirugias_previas: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    observaciones_generales: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
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

    paciente: Mapped["Patient"] = relationship(
        back_populates="historial_clinico",
    )
    consultas: Mapped[list["Consultation"]] = relationship(
        back_populates="historial",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
