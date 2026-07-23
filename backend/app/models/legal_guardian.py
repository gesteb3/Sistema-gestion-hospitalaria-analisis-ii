from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.patient import Patient


class LegalGuardian(Base):
    __tablename__ = "responsables_legales"

    responsable_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    paciente_id: Mapped[int] = mapped_column(
        ForeignKey(
            "pacientes.paciente_id",
            ondelete="CASCADE",
        ),
        nullable=False,
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
    identificacion: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    parentesco: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    telefono: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    correo: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    es_principal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    paciente: Mapped["Patient"] = relationship(
        back_populates="responsables_legales",
    )

    @property
    def principal(self) -> bool:
        return self.es_principal == 1
