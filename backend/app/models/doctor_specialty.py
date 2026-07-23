from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base


medico_especialidades = Table(
    "medico_especialidades",
    Base.metadata,
    Column(
        "medico_id",
        Integer,
        ForeignKey("medicos.medico_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "especialidad_id",
        Integer,
        ForeignKey(
            "especialidades.especialidad_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)
