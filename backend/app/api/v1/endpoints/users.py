from fastapi import APIRouter, status

from app.api.dependencies import (
    AdminUserDependency,
    DatabaseDependency,
)
from app.repositories.user_repository import list_users
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import create_user, role_names


router = APIRouter(
    prefix="/users",
    tags=["Usuarios"],
)


def to_user_response(user) -> UserResponse:
    return UserResponse(
        usuario_id=user.usuario_id,
        nombre_usuario=user.nombre_usuario,
        correo=user.correo,
        nombres=user.nombres,
        apellidos=user.apellidos,
        activo=user.esta_activo,
        roles=role_names(user),
        fecha_creacion=user.fecha_creacion,
        ultimo_acceso=user.ultimo_acceso,
    )


@router.get(
    "",
    response_model=list[UserResponse],
)
def read_users(
    database: DatabaseDependency,
    _: AdminUserDependency,
) -> list[UserResponse]:
    return [
        to_user_response(user)
        for user in list_users(database)
    ]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserCreate,
    database: DatabaseDependency,
    _: AdminUserDependency,
) -> UserResponse:
    user = create_user(database, payload)
    return to_user_response(user)
