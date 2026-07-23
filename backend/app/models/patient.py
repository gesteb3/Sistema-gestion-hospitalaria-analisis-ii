from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Identity, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.legal_guardian import LegalGuardian


class Patient(Base):
    __tablename__ = "pacientes"

    paciente_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    numero_expediente: Mapped[str | None] = mapped_column(
        String(25),
        unique=True,
        nullable=True,
        index=True,
    )
    nombres: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    apellidos: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    fecha_nacimiento: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    sexo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    identificacion: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True,
        index=True,
    )
    telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    correo: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    direccion: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )
    estado: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
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

    responsables_legales: Mapped[list["LegalGuardian"]] = relationship(
        back_populates="paciente",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="LegalGuardian.responsable_id",
    )
    citas: Mapped[list["Appointment"]] = relationship(
        back_populates="paciente",
        lazy="selectin",
    )

    @property
    def esta_activo(self) -> bool:
        return self.estado == 1
