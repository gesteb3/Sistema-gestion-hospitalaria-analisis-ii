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
    from app.models.appointment import Appointment
    from app.models.clinical_history import ClinicalHistory
    from app.models.diagnosis import Diagnosis
    from app.models.doctor import Doctor
    from app.models.treatment import Treatment
    from app.models.vital_signs import VitalSigns


class Consultation(Base):
    __tablename__ = "consultas"

    consulta_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    historial_id: Mapped[int] = mapped_column(
        ForeignKey(
            "historiales_clinicos.historial_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    cita_id: Mapped[int] = mapped_column(
        ForeignKey("citas.cita_id"),
        unique=True,
        nullable=False,
        index=True,
    )
    medico_id: Mapped[int] = mapped_column(
        ForeignKey("medicos.medico_id"),
        nullable=False,
        index=True,
    )
    motivo_consulta: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    sintomas: Mapped[str | None] = mapped_column(
        String(1500),
        nullable=True,
    )
    evaluacion_clinica: Mapped[str] = mapped_column(
        String(3000),
        nullable=False,
    )
    indicaciones_generales: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    notas_medicas: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    fecha_atencion: Mapped[datetime] = mapped_column(
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

    historial: Mapped["ClinicalHistory"] = relationship(
        back_populates="consultas",
    )
    cita: Mapped["Appointment"] = relationship(
        back_populates="consulta",
        lazy="joined",
    )
    medico: Mapped["Doctor"] = relationship(
        back_populates="consultas",
        lazy="joined",
    )
    signos_vitales: Mapped["VitalSigns | None"] = relationship(
        back_populates="consulta",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
    diagnosticos: Mapped[list["Diagnosis"]] = relationship(
        back_populates="consulta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tratamientos: Mapped[list["Treatment"]] = relationship(
        back_populates="consulta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
