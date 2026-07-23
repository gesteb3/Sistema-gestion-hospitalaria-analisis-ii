from datetime import datetime

from sqlalchemy import (
    DateTime,
    Identity,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "bitacora_auditoria"

    bitacora_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    usuario_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )
    nombre_usuario: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    accion: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    modulo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    metodo_http: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    ruta: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )
    codigo_respuesta: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    exitoso: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    direccion_ip: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )
    duracion_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    detalle: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    fecha_evento: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        index=True,
    )

    @property
    def fue_exitoso(self) -> bool:
        return self.exitoso == 1
