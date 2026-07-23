import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine
from app.models import (
    LabTestType,
    Medication,
    Role,
    Specialty,
    User,
)


logger = logging.getLogger(__name__)
settings = get_settings()


DEFAULT_ROLES = {
    "ADMINISTRADOR": "Gestiona usuarios, roles, médicos y reportes.",
    "RECEPCIONISTA": "Registra pacientes y programa citas.",
    "MEDICO": "Consulta historiales y registra atención médica.",
    "ENFERMERO": "Registra signos vitales y observaciones.",
    "LABORATORIO": "Registra órdenes y resultados de exámenes.",
    "FARMACIA": "Consulta recetas y controla medicamentos.",
    "CONTABILIDAD": "Registra pagos y consulta reportes financieros.",
    "PACIENTE": "Consulta citas y resultados autorizados.",
    "AUDITOR": "Consulta la bitácora de operaciones.",
}

DEFAULT_SPECIALTIES = {
    "Medicina General": (
        "Atención primaria y evaluación general del paciente."
    ),
    "Pediatría": (
        "Atención médica de niños y adolescentes."
    ),
    "Medicina Interna": (
        "Diagnóstico y tratamiento de enfermedades en adultos."
    ),
    "Ginecología": (
        "Atención de la salud del sistema reproductivo femenino."
    ),
    "Cardiología": (
        "Diagnóstico y tratamiento del sistema cardiovascular."
    ),
}

DEFAULT_MEDICATIONS = [
    {
        "codigo": "MED-001",
        "nombre": "Paracetamol",
        "principio_activo": "Acetaminofén",
        "concentracion": "500 mg",
        "presentacion": "Tabletas",
        "unidad": "TABLETA",
        "stock_actual": 100,
        "stock_minimo": 20,
        "precio_unitario": Decimal("0.50"),
    },
    {
        "codigo": "MED-002",
        "nombre": "Ibuprofeno",
        "principio_activo": "Ibuprofeno",
        "concentracion": "400 mg",
        "presentacion": "Tabletas",
        "unidad": "TABLETA",
        "stock_actual": 80,
        "stock_minimo": 15,
        "precio_unitario": Decimal("0.75"),
    },
    {
        "codigo": "MED-003",
        "nombre": "Amoxicilina",
        "principio_activo": "Amoxicilina",
        "concentracion": "500 mg",
        "presentacion": "Cápsulas",
        "unidad": "CAPSULA",
        "stock_actual": 60,
        "stock_minimo": 20,
        "precio_unitario": Decimal("1.25"),
    },
]

DEFAULT_LAB_TESTS = [
    {
        "codigo": "LAB-001",
        "nombre": "Hemograma completo",
        "descripcion": (
            "Evaluación general de células sanguíneas."
        ),
        "muestra_requerida": "Sangre",
        "tiempo_estimado_horas": 6,
        "precio": Decimal("75.00"),
    },
    {
        "codigo": "LAB-002",
        "nombre": "Glucosa en sangre",
        "descripcion": (
            "Medición de glucosa sanguínea."
        ),
        "muestra_requerida": "Sangre",
        "tiempo_estimado_horas": 4,
        "precio": Decimal("35.00"),
    },
    {
        "codigo": "LAB-003",
        "nombre": "Examen general de orina",
        "descripcion": (
            "Análisis físico, químico y microscópico."
        ),
        "muestra_requerida": "Orina",
        "tiempo_estimado_horas": 6,
        "precio": Decimal("45.00"),
    },
]


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_roles(database: Session) -> None:
    existing_names = set(
        database.scalars(select(Role.nombre)).all()
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


def seed_specialties(database: Session) -> None:
    existing_names = set(
        database.scalars(select(Specialty.nombre)).all()
    )

    for name, description in DEFAULT_SPECIALTIES.items():
        if name not in existing_names:
            database.add(
                Specialty(
                    nombre=name,
                    descripcion=description,
                    estado=1,
                )
            )

    database.commit()


def seed_medications(database: Session) -> None:
    existing_codes = set(
        database.scalars(select(Medication.codigo)).all()
    )

    for values in DEFAULT_MEDICATIONS:
        if values["codigo"] not in existing_codes:
            database.add(
                Medication(
                    **values,
                    estado=1,
                )
            )

    database.commit()


def seed_lab_tests(database: Session) -> None:
    existing_codes = set(
        database.scalars(select(LabTestType.codigo)).all()
    )

    for values in DEFAULT_LAB_TESTS:
        if values["codigo"] not in existing_codes:
            database.add(
                LabTestType(
                    **values,
                    estado=1,
                )
            )

    database.commit()


def seed_admin(database: Session) -> None:
    existing_admin = database.scalar(
        select(User).where(
            User.nombre_usuario == settings.admin_username
        )
    )

    administrator_role = database.scalar(
        select(Role).where(Role.nombre == "ADMINISTRADOR")
    )

    if administrator_role is None:
        raise RuntimeError("No se encontró el rol ADMINISTRADOR.")

    if existing_admin:
        changed = False
        valid_email = settings.admin_email.lower()

        if existing_admin.correo != valid_email:
            existing_admin.correo = valid_email
            changed = True

        if administrator_role not in existing_admin.roles:
            existing_admin.roles.append(administrator_role)
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
        contrasena_hash=hash_password(settings.admin_password),
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
        seed_specialties(database)
        seed_medications(database)
        seed_lab_tests(database)
        seed_admin(database)
