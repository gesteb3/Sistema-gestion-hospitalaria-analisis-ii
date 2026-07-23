from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    nombre_usuario: str = Field(min_length=4, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    correo: EmailStr
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    roles: list[str] = Field(min_length=1)

    @field_validator("nombre_usuario")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if " " in cleaned:
            raise ValueError("El nombre de usuario no puede contener espacios.")
        return cleaned

    @field_validator("roles")
    @classmethod
    def normalize_roles(cls, value: list[str]) -> list[str]:
        roles = sorted({role.strip().upper() for role in value if role.strip()})
        if not roles:
            raise ValueError("Debe asignarse al menos un rol.")
        return roles


class RoleResponse(BaseModel):
    rol_id: int
    nombre: str
    descripcion: str | None
    activo: bool


class UserResponse(BaseModel):
    usuario_id: int
    nombre_usuario: str
    correo: EmailStr
    nombres: str
    apellidos: str
    activo: bool
    roles: list[str]
    fecha_creacion: datetime
    ultimo_acceso: datetime | None

    model_config = ConfigDict(from_attributes=True)
