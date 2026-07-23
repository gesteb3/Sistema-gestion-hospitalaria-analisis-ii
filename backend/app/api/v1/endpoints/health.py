from fastapi import APIRouter, Response, status

from app.core.config import get_settings
from app.db.session import check_database_connection

router = APIRouter(tags=["Sistema"])
settings = get_settings()


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@router.get("/health/database")
def database_health(response: Response) -> dict[str, str]:
    connected = check_database_connection()

    if not connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "database": "Oracle Database",
            "message": "No fue posible conectar con Oracle.",
        }

    return {
        "status": "ok",
        "database": "Oracle Database",
        "service_name": settings.oracle_service,
        "message": "Conexión con Oracle establecida correctamente.",
    }
