from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    bitacora_id: int
    usuario_id: int | None
    nombre_usuario: str | None
    accion: str
    modulo: str
    metodo_http: str
    ruta: str
    codigo_respuesta: int
    exitoso: bool
    direccion_ip: str | None
    duracion_ms: int
    detalle: str | None
    fecha_evento: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
