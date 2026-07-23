from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Identity, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.association import usuario_roles

if TYPE_CHECKING:
    from app.models.role import Role


class User(Base):
    __tablename__ = "usuarios"

    usuario_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    nombre_usuario: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    contrasena_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    correo: Mapped[str] = mapped_column(
        String(150),
        unique=True,
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
    activo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    intentos_fallidos: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    ultimo_acceso: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    roles: Mapped[list["Role"]] = relationship(
        secondary=usuario_roles,
        back_populates="usuarios",
        lazy="selectin",
    )

    @property
    def esta_activo(self) -> bool:
        return self.activo == 1
