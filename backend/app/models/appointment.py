from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
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
    from app.models.doctor import Doctor
    from app.models.patient import Patient


class Appointment(Base):
    __tablename__ = "citas"

    cita_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("pacientes.paciente_id"),
        nullable=False,
        index=True,
    )
    medico_id: Mapped[int] = mapped_column(
        ForeignKey("medicos.medico_id"),
        nullable=False,
        index=True,
    )
    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    hora: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
    )
    duracion_minutos: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    motivo: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    observaciones: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PROGRAMADA",
        index=True,
    )
    motivo_cancelacion: Mapped[str | None] = mapped_column(
        String(500),
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
        back_populates="citas",
        lazy="joined",
    )
    medico: Mapped["Doctor"] = relationship(
        back_populates="citas",
        lazy="joined",
    )
    consulta: Mapped["Consultation | None"] = relationship(
        back_populates="cita",
        uselist=False,
        lazy="selectin",
    )
