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


class Diagnosis(Base):
    __tablename__ = "diagnosticos"

    diagnostico_id: Mapped[int] = mapped_column(
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
    codigo_cie10: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True,
    )
    descripcion: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PRESUNTIVO",
    )
    es_principal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    consulta: Mapped["Consultation"] = relationship(
        back_populates="diagnosticos",
    )

    @property
    def principal(self) -> bool:
        return self.es_principal == 1
