import logging
from time import perf_counter

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.utils.audit import (
    action_from_method,
    module_from_path,
    should_audit_path,
)


logger = logging.getLogger(__name__)
settings = get_settings()


def extract_identity(
    request: Request,
) -> tuple[int | None, str | None]:
    authorization = request.headers.get(
        "Authorization",
        "",
    )

    if not authorization.startswith("Bearer "):
        return None, None

    token = authorization.removeprefix(
        "Bearer "
    ).strip()

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
        username = payload.get("username")
        return user_id, username
    except (ValueError, TypeError, KeyError):
        return None, None


def save_audit_log(
    *,
    user_id: int | None,
    username: str | None,
    method: str,
    path: str,
    status_code: int,
    client_ip: str | None,
    duration_ms: int,
    detail: str | None,
) -> None:
    try:
        with SessionLocal() as database:
            database.add(
                AuditLog(
                    usuario_id=user_id,
                    nombre_usuario=username,
                    accion=action_from_method(method),
                    modulo=module_from_path(
                        path,
                        settings.api_v1_prefix,
                    ),
                    metodo_http=method.upper(),
                    ruta=path[:500],
                    codigo_respuesta=status_code,
                    exitoso=int(status_code < 400),
                    direccion_ip=client_ip,
                    duracion_ms=duration_ms,
                    detalle=(
                        detail[:1000]
                        if detail is not None
                        else None
                    ),
                )
            )
            database.commit()
    except Exception:
        logger.exception(
            "No fue posible guardar el evento de auditoría."
        )


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        path = request.url.path

        if not should_audit_path(path):
            return await call_next(request)

        user_id, username = extract_identity(request)
        client_ip = (
            request.client.host
            if request.client is not None
            else None
        )
        started_at = perf_counter()
        status_code = 500
        detail = None

        try:
            response = await call_next(request)
            status_code = response.status_code

            if status_code >= 400:
                detail = (
                    f"Solicitud finalizada con código "
                    f"{status_code}."
                )

            return response
        except Exception as exc:
            detail = (
                f"Error interno: {type(exc).__name__}"
            )
            raise
        finally:
            elapsed_ms = max(
                0,
                int(
                    (perf_counter() - started_at)
                    * 1000
                ),
            )
            save_audit_log(
                user_id=user_id,
                username=username,
                method=request.method,
                path=path,
                status_code=status_code,
                client_ip=client_ip,
                duration_ms=elapsed_ms,
                detail=detail,
            )
