import math
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import (
    list_audit_logs,
)
from app.schemas.audit import (
    AuditLogListResponse,
    AuditLogResponse,
)


def audit_log_to_response(
    record: AuditLog,
) -> AuditLogResponse:
    return AuditLogResponse(
        bitacora_id=record.bitacora_id,
        usuario_id=record.usuario_id,
        nombre_usuario=record.nombre_usuario,
        accion=record.accion,
        modulo=record.modulo,
        metodo_http=record.metodo_http,
        ruta=record.ruta,
        codigo_respuesta=record.codigo_respuesta,
        exitoso=record.fue_exitoso,
        direccion_ip=record.direccion_ip,
        duracion_ms=record.duracion_ms,
        detalle=record.detalle,
        fecha_evento=record.fecha_evento,
    )


def read_audit_logs(
    database: Session,
    username: str | None,
    module: str | None,
    method: str | None,
    successful: bool | None,
    date_from: datetime | None,
    date_to: datetime | None,
    page: int,
    page_size: int,
) -> AuditLogListResponse:
    records, total = list_audit_logs(
        database=database,
        username=username,
        module=module,
        method=method,
        successful=successful,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )

    return AuditLogListResponse(
        items=[
            audit_log_to_response(record)
            for record in records
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(
            math.ceil(total / page_size)
            if total > 0
            else 0
        ),
    )
