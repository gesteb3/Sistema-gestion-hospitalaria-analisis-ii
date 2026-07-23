from decimal import Decimal

from pydantic import BaseModel


class StatusCount(BaseModel):
    estado: str
    cantidad: int


class DashboardReportResponse(BaseModel):
    pacientes_activos: int
    medicos_activos: int
    citas_totales: int
    citas_programadas: int
    consultas_realizadas: int
    ordenes_laboratorio_pendientes: int
    recetas_emitidas: int
    medicamentos_stock_bajo: int
    facturas_pendientes: int
    total_facturado: Decimal
    total_pagado: Decimal
    saldo_pendiente: Decimal


class ClinicalReportResponse(BaseModel):
    pacientes_activos: int
    consultas_realizadas: int
    citas_por_estado: list[StatusCount]
    ordenes_laboratorio_por_estado: list[StatusCount]
    recetas_por_estado: list[StatusCount]


class FinancialReportResponse(BaseModel):
    total_facturado: Decimal
    total_pagado: Decimal
    saldo_pendiente: Decimal
    facturas_por_estado: list[StatusCount]
    cantidad_pagos: int
    monto_promedio_factura: Decimal


class SystemReportResponse(BaseModel):
    usuarios_activos: int
    medicos_activos: int
    pacientes_activos: int
    eventos_auditoria: int
    eventos_exitosos: int
    eventos_fallidos: int
