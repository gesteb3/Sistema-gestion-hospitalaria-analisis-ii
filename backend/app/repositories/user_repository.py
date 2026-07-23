from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.role import Role
from app.models.user import User


def get_user_by_id(database: Session, usuario_id: int) -> User | None:
    statement = (
        select(User)
        .options(selectinload(User.roles))
        .where(User.usuario_id == usuario_id)
    )
    return database.scalar(statement)


def get_user_by_username(database: Session, username: str) -> User | None:
    statement = (
        select(User)
        .options(selectinload(User.roles))
        .where(
            func.lower(User.nombre_usuario) == username.strip().lower()
        )
    )
    return database.scalar(statement)


def get_user_by_email(database: Session, email: str) -> User | None:
    statement = (
        select(User)
        .options(selectinload(User.roles))
        .where(func.lower(User.correo) == email.strip().lower())
    )
    return database.scalar(statement)


def list_users(database: Session) -> list[User]:
    statement = (
        select(User)
        .options(selectinload(User.roles))
        .order_by(User.usuario_id)
    )
    return list(database.scalars(statement).all())


def get_roles_by_names(
    database: Session,
    role_names: list[str],
) -> list[Role]:
    normalized = [name.strip().upper() for name in role_names]
    statement = select(Role).where(Role.nombre.in_(normalized))
    return list(database.scalars(statement).all())
