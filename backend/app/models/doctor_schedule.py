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
    from app.models.doctor import Doctor


class DoctorSchedule(Base):
    __tablename__ = "horarios_medicos"

    horario_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    medico_id: Mapped[int] = mapped_column(
        ForeignKey(
            "medicos.medico_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    dia_semana: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    hora_inicio: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
    )
    hora_fin: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
    )
    duracion_cita_minutos: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
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

    medico: Mapped["Doctor"] = relationship(
        back_populates="horarios",
    )

    @property
    def esta_activo(self) -> bool:
        return self.estado == 1
