from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import (
    CurrentUserDependency,
    DatabaseDependency,
)
from app.schemas.auth import TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import (
    authenticate_user,
    build_token_response,
    role_names,
)


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    database: DatabaseDependency,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    user = authenticate_user(
        database,
        form_data.username,
        form_data.password,
    )
    return build_token_response(user)


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: CurrentUserDependency,
) -> UserResponse:
    return UserResponse(
        usuario_id=current_user.usuario_id,
        nombre_usuario=current_user.nombre_usuario,
        correo=current_user.correo,
        nombres=current_user.nombres,
        apellidos=current_user.apellidos,
        activo=current_user.esta_activo,
        roles=role_names(current_user),
        fecha_creacion=current_user.fecha_creacion,
        ultimo_acceso=current_user.ultimo_acceso,
    )
