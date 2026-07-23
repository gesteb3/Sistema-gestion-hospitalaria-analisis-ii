from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base


usuario_roles = Table(
    "usuario_roles",
    Base.metadata,
    Column(
        "usuario_id",
        Integer,
        ForeignKey(
            "usuarios.usuario_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "rol_id",
        Integer,
        ForeignKey(
            "roles.rol_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)