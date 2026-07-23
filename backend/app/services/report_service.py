from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.models.consultation import Consultation
from app.models.doctor import Doctor
from app.models.invoice import Invoice
from app.models.lab_order import LabOrder
from app.models.medication import Medication
from app.models.patient import Patient
from app.models.payment import Payment
from app.models.prescription import Prescription
from app.models.user import User
from app.schemas.reports import (
    ClinicalReportResponse,
    DashboardReportResponse,
    FinancialReportResponse,
    StatusCount,
    SystemReportResponse,
)
from app.utils.billing import money


def scalar_count(
    database: Session,
    statement,
) -> int:
    return int(database.scalar(statement) or 0)


def grouped_status_counts(
    database: Session,
    model,
    status_column,
) -> list[StatusCount]:
    statement = (
        select(
            status_column,
            func.count(),
        )
        .select_from(model)
        .group_by(status_column)
        .order_by(status_column)
    )

    return [
        StatusCount(
            estado=str(status),
            cantidad=int(quantity),
        )
        for status, quantity
        in database.execute(statement).all()
    ]


def sum_invoice_field(
    database: Session,
    field,
) -> Decimal:
    value = database.scalar(
        select(func.coalesce(func.sum(field), 0)).where(
            Invoice.estado != "ANULADA"
        )
    )
    return money(value or 0)


def read_dashboard_report(
    database: Session,
) -> DashboardReportResponse:
    return DashboardReportResponse(
        pacientes_activos=scalar_count(
            database,
            select(func.count(Patient.paciente_id)).where(
                Patient.estado == 1
            ),
        ),
        medicos_activos=scalar_count(
            database,
            select(func.count(Doctor.medico_id)).where(
                Doctor.estado == 1
            ),
        ),
        citas_totales=scalar_count(
            database,
            select(func.count(Appointment.cita_id)),
        ),
        citas_programadas=scalar_count(
            database,
            select(func.count(Appointment.cita_id)).where(
                Appointment.estado.in_(
                    ["PROGRAMADA", "CONFIRMADA"]
                )
            ),
        ),
        consultas_realizadas=scalar_count(
            database,
            select(func.count(Consultation.consulta_id)),
        ),
        ordenes_laboratorio_pendientes=scalar_count(
            database,
            select(
                func.count(
                    LabOrder.orden_laboratorio_id
                )
            ).where(
                LabOrder.estado.in_(
                    ["SOLICITADA", "EN_PROCESO"]
                )
            ),
        ),
        recetas_emitidas=scalar_count(
            database,
            select(
                func.count(Prescription.receta_id)
            ).where(
                Prescription.estado == "EMITIDA"
            ),
        ),
        medicamentos_stock_bajo=scalar_count(
            database,
            select(
                func.count(Medication.medicamento_id)
            ).where(
                Medication.estado == 1,
                Medication.stock_actual
                <= Medication.stock_minimo,
            ),
        ),
        facturas_pendientes=scalar_count(
            database,
            select(func.count(Invoice.factura_id)).where(
                Invoice.estado.in_(
                    ["PENDIENTE", "PARCIAL"]
                )
            ),
        ),
        total_facturado=sum_invoice_field(
            database,
            Invoice.total,
        ),
        total_pagado=sum_invoice_field(
            database,
            Invoice.total_pagado,
        ),
        saldo_pendiente=sum_invoice_field(
            database,
            Invoice.saldo_pendiente,
        ),
    )


def read_clinical_report(
    database: Session,
) -> ClinicalReportResponse:
    return ClinicalReportResponse(
        pacientes_activos=scalar_count(
            database,
            select(func.count(Patient.paciente_id)).where(
                Patient.estado == 1
            ),
        ),
        consultas_realizadas=scalar_count(
            database,
            select(func.count(Consultation.consulta_id)),
        ),
        citas_por_estado=grouped_status_counts(
            database,
            Appointment,
            Appointment.estado,
        ),
        ordenes_laboratorio_por_estado=(
            grouped_status_counts(
                database,
                LabOrder,
                LabOrder.estado,
            )
        ),
        recetas_por_estado=grouped_status_counts(
            database,
            Prescription,
            Prescription.estado,
        ),
    )


def read_financial_report(
    database: Session,
) -> FinancialReportResponse:
    invoice_count = scalar_count(
        database,
        select(func.count(Invoice.factura_id)).where(
            Invoice.estado != "ANULADA"
        ),
    )
    total_billed = sum_invoice_field(
        database,
        Invoice.total,
    )

    average = (
        money(total_billed / invoice_count)
        if invoice_count > 0
        else Decimal("0.00")
    )

    return FinancialReportResponse(
        total_facturado=total_billed,
        total_pagado=sum_invoice_field(
            database,
            Invoice.total_pagado,
        ),
        saldo_pendiente=sum_invoice_field(
            database,
            Invoice.saldo_pendiente,
        ),
        facturas_por_estado=grouped_status_counts(
            database,
            Invoice,
            Invoice.estado,
        ),
        cantidad_pagos=scalar_count(
            database,
            select(func.count(Payment.pago_id)).where(
                Payment.estado == "APLICADO"
            ),
        ),
        monto_promedio_factura=average,
    )


def read_system_report(
    database: Session,
) -> SystemReportResponse:
    return SystemReportResponse(
        usuarios_activos=scalar_count(
            database,
            select(func.count(User.usuario_id)).where(
                User.activo == 1
            ),
        ),
        medicos_activos=scalar_count(
            database,
            select(func.count(Doctor.medico_id)).where(
                Doctor.estado == 1
            ),
        ),
        pacientes_activos=scalar_count(
            database,
            select(func.count(Patient.paciente_id)).where(
                Patient.estado == 1
            ),
        ),
        eventos_auditoria=scalar_count(
            database,
            select(func.count(AuditLog.bitacora_id)),
        ),
        eventos_exitosos=scalar_count(
            database,
            select(func.count(AuditLog.bitacora_id)).where(
                AuditLog.exitoso == 1
            ),
        ),
        eventos_fallidos=scalar_count(
            database,
            select(func.count(AuditLog.bitacora_id)).where(
                AuditLog.exitoso == 0
            ),
        ),
    )
