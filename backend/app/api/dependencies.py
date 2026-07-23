from collections.abc import Callable
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


def require_roles(*allowed_roles: str) -> Callable:
    normalized_roles = {
        role.strip().upper()
        for role in allowed_roles
    }

    def dependency(
        current_user: CurrentUserDependency,
    ) -> User:
        current_roles = {
            role.nombre
            for role in current_user.roles
            if role.activo == 1
        }

        if not current_roles.intersection(normalized_roles):
            required = ", ".join(sorted(normalized_roles))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de estos roles: {required}.",
            )

        return current_user

    return dependency


def require_admin(
    current_user: CurrentUserDependency,
) -> User:
    return require_roles("ADMINISTRADOR")(current_user)


AdminUserDependency = Annotated[User, Depends(require_admin)]

PatientReaderDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "RECEPCIONISTA",
            "MEDICO",
            "ENFERMERO",
            "LABORATORIO",
            "CONTABILIDAD",
            "AUDITOR",
        )
    ),
]

PatientWriterDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "RECEPCIONISTA",
        )
    ),
]

DoctorReaderDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "RECEPCIONISTA",
            "MEDICO",
            "ENFERMERO",
            "LABORATORIO",
            "AUDITOR",
        )
    ),
]

DoctorWriterDependency = Annotated[
    User,
    Depends(
        require_roles("ADMINISTRADOR")
    ),
]

AppointmentReaderDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "RECEPCIONISTA",
            "MEDICO",
            "ENFERMERO",
            "AUDITOR",
        )
    ),
]

AppointmentWriterDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "RECEPCIONISTA",
        )
    ),
]

AppointmentStatusDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "RECEPCIONISTA",
            "MEDICO",
        )
    ),
]

ClinicalReaderDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "MEDICO",
            "ENFERMERO",
            "LABORATORIO",
            "AUDITOR",
        )
    ),
]

ClinicalWriterDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "MEDICO",
        )
    ),
]

VitalSignsWriterDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "MEDICO",
            "ENFERMERO",
        )
    ),
]

PharmacyReaderDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "MEDICO",
            "FARMACIA",
            "AUDITOR",
        )
    ),
]

PharmacyWriterDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "FARMACIA",
        )
    ),
]

PrescriptionWriterDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "MEDICO",
        )
    ),
]

LaboratoryReaderDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "MEDICO",
            "LABORATORIO",
            "AUDITOR",
        )
    ),
]

LaboratoryOrderWriterDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "MEDICO",
        )
    ),
]

LaboratoryProcessorDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "LABORATORIO",
        )
    ),
]

BillingReaderDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "CONTABILIDAD",
            "AUDITOR",
        )
    ),
]

BillingWriterDependency = Annotated[
    User,
    Depends(
        require_roles(
            "ADMINISTRADOR",
            "CONTABILIDAD",
        )
    ),
]
