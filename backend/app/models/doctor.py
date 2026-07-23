from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Identity, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.doctor_specialty import medico_especialidades

if TYPE_CHECKING:
    from app.models.doctor_schedule import DoctorSchedule
    from app.models.specialty import Specialty


class Doctor(Base):
    __tablename__ = "medicos"

    medico_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    nombres: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    apellidos: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    numero_colegiado: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )
    telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    correo: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
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

    especialidades: Mapped[list["Specialty"]] = relationship(
        secondary=medico_especialidades,
        back_populates="medicos",
        lazy="selectin",
    )
    horarios: Mapped[list["DoctorSchedule"]] = relationship(
        back_populates="medico",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def esta_activo(self) -> bool:
        return self.estado == 1
