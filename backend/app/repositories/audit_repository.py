from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def list_audit_logs(
    database: Session,
    username: str | None,
    module: str | None,
    method: str | None,
    successful: bool | None,
    date_from: datetime | None,
    date_to: datetime | None,
    page: int,
    page_size: int,
) -> tuple[list[AuditLog], int]:
    filters = []

    if username:
        filters.append(
            func.lower(AuditLog.nombre_usuario)
            == username.strip().lower()
        )

    if module:
        filters.append(
            func.lower(AuditLog.modulo)
            == module.strip().lower()
        )

    if method:
        filters.append(
            AuditLog.metodo_http
            == method.strip().upper()
        )

    if successful is not None:
        filters.append(
            AuditLog.exitoso == int(successful)
        )

    if date_from is not None:
        filters.append(
            AuditLog.fecha_evento >= date_from
        )

    if date_to is not None:
        filters.append(
            AuditLog.fecha_evento <= date_to
        )

    count_statement = select(
        func.count(AuditLog.bitacora_id)
    )
    statement = (
        select(AuditLog)
        .order_by(
            AuditLog.fecha_evento.desc(),
            AuditLog.bitacora_id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if filters:
        count_statement = count_statement.where(*filters)
        statement = statement.where(*filters)

    total = int(database.scalar(count_statement) or 0)
    records = list(database.scalars(statement).all())

    return records, total
