from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Identity, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.doctor_specialty import medico_especialidades

if TYPE_CHECKING:
    from app.models.doctor import Doctor


class Specialty(Base):
    __tablename__ = "especialidades"

    especialidad_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    nombre: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    descripcion: Mapped[str | None] = mapped_column(
        String(300),
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

    medicos: Mapped[list["Doctor"]] = relationship(
        secondary=medico_especialidades,
        back_populates="especialidades",
    )

    @property
    def esta_activa(self) -> bool:
        return self.estado == 1
