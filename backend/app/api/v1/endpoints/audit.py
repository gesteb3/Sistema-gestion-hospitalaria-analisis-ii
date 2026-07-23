from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import (
    AuditReaderDependency,
    DatabaseDependency,
)
from app.schemas.audit import AuditLogListResponse
from app.services.audit_service import read_audit_logs


router = APIRouter(
    prefix="/audit-logs",
    tags=["Auditoría"],
)


@router.get(
    "",
    response_model=AuditLogListResponse,
)
def list_system_audit_logs(
    database: DatabaseDependency,
    _: AuditReaderDependency,
    username: str | None = None,
    module: str | None = None,
    method: str | None = None,
    successful: bool | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> AuditLogListResponse:
    return read_audit_logs(
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
