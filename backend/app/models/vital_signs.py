from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Float,
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


class VitalSigns(Base):
    __tablename__ = "signos_vitales"

    signo_vital_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    consulta_id: Mapped[int] = mapped_column(
        ForeignKey(
            "consultas.consulta_id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )
    temperatura_c: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    presion_sistolica: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    presion_diastolica: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    frecuencia_cardiaca: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    frecuencia_respiratoria: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    saturacion_oxigeno: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    peso_kg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    estatura_cm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    imc: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    observaciones: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    consulta: Mapped["Consultation"] = relationship(
        back_populates="signos_vitales",
    )
