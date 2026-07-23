from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import (
    get_roles_by_names,
    get_user_by_email,
    get_user_by_username,
)
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate


settings = get_settings()


def role_names(user: User) -> list[str]:
    return sorted(role.nombre for role in user.roles if role.activo == 1)


def authenticate_user(
    database: Session,
    username: str,
    password: str,
) -> User:
    user = get_user_by_username(database, username)

    if user is None or not verify_password(
        password,
        user.contrasena_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta se encuentra desactivada.",
        )

    if user.bloqueado_hasta and user.bloqueado_hasta > datetime.now():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="La cuenta se encuentra bloqueada temporalmente.",
        )

    user.ultimo_acceso = datetime.now()
    user.intentos_fallidos = 0
    database.commit()
    database.refresh(user)

    return user


def build_token_response(user: User) -> TokenResponse:
    roles = role_names(user)

    token = create_access_token(
        subject=str(user.usuario_id),
        additional_claims={
            "username": user.nombre_usuario,
            "roles": roles,
        },
    )

    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.access_token_expire_minutes,
        usuario=user.nombre_usuario,
        roles=roles,
    )


def create_user(
    database: Session,
    payload: UserCreate,
) -> User:
    if get_user_by_username(database, payload.nombre_usuario):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario ya está registrado.",
        )

    if get_user_by_email(database, str(payload.correo)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado.",
        )

    roles = get_roles_by_names(database, payload.roles)
    found_names = {role.nombre for role in roles}
    missing = sorted(set(payload.roles) - found_names)

    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles inexistentes: {', '.join(missing)}.",
        )

    user = User(
        nombre_usuario=payload.nombre_usuario,
        contrasena_hash=hash_password(payload.password),
        correo=str(payload.correo).lower(),
        nombres=payload.nombres.strip(),
        apellidos=payload.apellidos.strip(),
        activo=1,
        roles=roles,
    )

    database.add(user)
    database.commit()
    database.refresh(user)

    return user
