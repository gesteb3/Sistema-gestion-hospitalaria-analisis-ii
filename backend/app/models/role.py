from typing import TYPE_CHECKING

from sqlalchemy import Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.association import usuario_roles

if TYPE_CHECKING:
    from app.models.user import User


class Role(Base):
    __tablename__ = "roles"

    rol_id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    nombre: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    descripcion: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )
    activo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    usuarios: Mapped[list["User"]] = relationship(
        secondary=usuario_roles,
        back_populates="roles",
    )
