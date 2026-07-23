from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import get_user_by_id


settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login"
)

DatabaseDependency = Annotated[Session, Depends(get_db)]
TokenDependency = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(
    database: DatabaseDependency,
    token: TokenDependency,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No fue posible validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        usuario_id = int(subject)
    except (ValueError, TypeError):
        raise credentials_exception

    user = get_user_by_id(database, usuario_id)

    if user is None or not user.esta_activo:
        raise credentials_exception

    return user


CurrentUserDependency = Annotated[User, Depends(get_current_user)]


def require_admin(
    current_user: CurrentUserDependency,
) -> User:
    role_names = {
        role.nombre
        for role in current_user.roles
        if role.activo == 1
    }

    if "ADMINISTRADOR" not in role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere el rol ADMINISTRADOR.",
        )

    return current_user


AdminUserDependency = Annotated[User, Depends(require_admin)]
