import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine
from app.models import Role, User


logger = logging.getLogger(__name__)
settings = get_settings()


DEFAULT_ROLES = {
    "ADMINISTRADOR": (
        "Gestiona usuarios, roles, médicos y reportes."
    ),
    "RECEPCIONISTA": (
        "Registra pacientes y programa citas."
    ),
    "MEDICO": (
        "Consulta historiales y registra atención médica."
    ),
    "ENFERMERO": (
        "Registra signos vitales y observaciones."
    ),
    "LABORATORIO": (
        "Registra órdenes y resultados de exámenes."
    ),
    "FARMACIA": (
        "Consulta recetas y controla medicamentos."
    ),
    "CONTABILIDAD": (
        "Registra pagos y consulta reportes financieros."
    ),
    "PACIENTE": (
        "Consulta citas y resultados autorizados."
    ),
    "AUDITOR": (
        "Consulta la bitácora de operaciones."
    ),
}


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_roles(database: Session) -> None:
    existing_names = set(
        database.scalars(
            select(Role.nombre)
        ).all()
    )

    for name, description in DEFAULT_ROLES.items():
        if name not in existing_names:
            database.add(
                Role(
                    nombre=name,
                    descripcion=description,
                    activo=1,
                )
            )

    database.commit()


def seed_admin(database: Session) -> None:
    existing_admin = database.scalar(
        select(User).where(
            User.nombre_usuario
            == settings.admin_username
        )
    )

    administrator_role = database.scalar(
        select(Role).where(
            Role.nombre == "ADMINISTRADOR"
        )
    )

    if administrator_role is None:
        raise RuntimeError(
            "No se encontró el rol ADMINISTRADOR."
        )

    if existing_admin:
        changed = False

        valid_email = settings.admin_email.lower()

        if existing_admin.correo != valid_email:
            existing_admin.correo = valid_email
            changed = True

        if administrator_role not in existing_admin.roles:
            existing_admin.roles.append(
                administrator_role
            )
            changed = True

        if changed:
            database.commit()
            database.refresh(existing_admin)

            logger.info(
                "Usuario administrador actualizado: %s",
                settings.admin_username,
            )

        return

    admin = User(
        nombre_usuario=settings.admin_username,
        contrasena_hash=hash_password(
            settings.admin_password
        ),
        correo=settings.admin_email.lower(),
        nombres=settings.admin_nombres,
        apellidos=settings.admin_apellidos,
        activo=1,
        roles=[administrator_role],
    )

    database.add(admin)
    database.commit()

    logger.info(
        "Usuario administrador inicial creado: %s",
        settings.admin_username,
    )


def initialize_database() -> None:
    create_tables()

    with Session(engine) as database:
        seed_roles(database)
        seed_admin(database)