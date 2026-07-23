import math
from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.payment import Payment
from app.repositories.billing_repository import (
    get_invoice_by_id,
    list_all_non_cancelled_invoices,
    list_invoices,
)
from app.repositories.clinical_repository import (
    get_consultation_by_id,
)
from app.repositories.patient_repository import (
    get_patient_by_id,
)
from app.schemas.billing import (
    BillingSummaryResponse,
    InvoiceCancel,
    InvoiceCreate,
    InvoiceItemResponse,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceUpdate,
    PaymentCreate,
    PaymentResponse,
)
from app.utils.billing import (
    build_invoice_number,
    calculate_invoice_totals,
    calculate_line_subtotal,
    invoice_status_from_balance,
    money,
)


def invoice_to_response(
    invoice: Invoice,
) -> InvoiceResponse:
    patient = invoice.paciente

    return InvoiceResponse(
        factura_id=invoice.factura_id,
        numero_factura=invoice.numero_factura or "",
        paciente_id=invoice.paciente_id,
        numero_expediente=(
            patient.numero_expediente or ""
        ),
        paciente_nombre=(
            f"{patient.nombres} {patient.apellidos}"
        ),
        consulta_id=invoice.consulta_id,
        nit=invoice.nit,
        nombre_facturacion=invoice.nombre_facturacion,
        direccion_facturacion=(
            invoice.direccion_facturacion
        ),
        subtotal=money(invoice.subtotal),
        descuento=money(invoice.descuento),
        total=money(invoice.total),
        total_pagado=money(invoice.total_pagado),
        saldo_pendiente=money(
            invoice.saldo_pendiente
        ),
        estado=invoice.estado,
        observaciones=invoice.observaciones,
        motivo_anulacion=invoice.motivo_anulacion,
        items=[
            InvoiceItemResponse(
                detalle_factura_id=(
                    item.detalle_factura_id
                ),
                tipo_servicio=item.tipo_servicio,
                descripcion=item.descripcion,
                cantidad=item.cantidad,
                precio_unitario=money(
                    item.precio_unitario
                ),
                subtotal=money(item.subtotal),
            )
            for item in sorted(
                invoice.items,
                key=lambda record: (
                    record.detalle_factura_id
                ),
            )
        ],
        pagos=[
            PaymentResponse(
                pago_id=payment.pago_id,
                monto=money(payment.monto),
                metodo_pago=payment.metodo_pago,
                referencia=payment.referencia,
                observaciones=payment.observaciones,
                estado=payment.estado,
                fecha_pago=payment.fecha_pago,
            )
            for payment in sorted(
                invoice.pagos,
                key=lambda record: record.pago_id,
            )
        ],
        fecha_emision=invoice.fecha_emision,
        fecha_actualizacion=(
            invoice.fecha_actualizacion
        ),
    )


def get_invoice_or_404(
    database: Session,
    invoice_id: int,
) -> Invoice:
    invoice = get_invoice_by_id(
        database,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada.",
        )

    return invoice


def create_invoice(
    database: Session,
    payload: InvoiceCreate,
) -> InvoiceResponse:
    patient = get_patient_by_id(
        database,
        payload.paciente_id,
    )

    if patient is None or not patient.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El paciente no existe o se encuentra inactivo."
            ),
        )

    if payload.consulta_id is not None:
        consultation = get_consultation_by_id(
            database,
            payload.consulta_id,
        )

        if consultation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta clínica no encontrada.",
            )

        if (
            consultation.cita.paciente_id
            != payload.paciente_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La consulta no corresponde al paciente."
                ),
            )

    line_subtotals = [
        calculate_line_subtotal(
            item.cantidad,
            item.precio_unitario,
        )
        for item in payload.items
    ]

    subtotal, total = calculate_invoice_totals(
        line_subtotals,
        payload.descuento,
    )

    if total <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El total de la factura debe ser mayor que cero."
            ),
        )

    invoice = Invoice(
        paciente_id=payload.paciente_id,
        consulta_id=payload.consulta_id,
        nit=payload.nit,
        nombre_facturacion=(
            payload.nombre_facturacion
        ),
        direccion_facturacion=(
            payload.direccion_facturacion
        ),
        subtotal=subtotal,
        descuento=money(payload.descuento),
        total=total,
        total_pagado=Decimal("0.00"),
        saldo_pendiente=total,
        estado="PENDIENTE",
        observaciones=payload.observaciones,
    )

    for item, line_subtotal in zip(
        payload.items,
        line_subtotals,
        strict=True,
    ):
        invoice.items.append(
            InvoiceItem(
                tipo_servicio=item.tipo_servicio,
                descripcion=item.descripcion,
                cantidad=item.cantidad,
                precio_unitario=money(
                    item.precio_unitario
                ),
                subtotal=line_subtotal,
            )
        )

    database.add(invoice)

    try:
        database.flush()
        invoice.numero_factura = build_invoice_number(
            invoice.factura_id,
            date.today().year,
        )
        database.commit()
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar la factura.",
        ) from exc

    stored = get_invoice_by_id(
        database,
        invoice.factura_id,
    )

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "La factura fue creada, pero no pudo recuperarse."
            ),
        )

    return invoice_to_response(stored)


def read_invoice(
    database: Session,
    invoice_id: int,
) -> InvoiceResponse:
    return invoice_to_response(
        get_invoice_or_404(
            database,
            invoice_id,
        )
    )


def read_invoices(
    database: Session,
    patient_id: int | None,
    invoice_status: str | None,
    page: int,
    page_size: int,
) -> InvoiceListResponse:
    normalized_status = (
        invoice_status.strip().upper()
        if invoice_status
        else None
    )

    invoices, total = list_invoices(
        database=database,
        patient_id=patient_id,
        invoice_status=normalized_status,
        page=page,
        page_size=page_size,
    )

    return InvoiceListResponse(
        items=[
            invoice_to_response(invoice)
            for invoice in invoices
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


def update_invoice(
    database: Session,
    invoice_id: int,
    payload: InvoiceUpdate,
) -> InvoiceResponse:
    invoice = get_invoice_or_404(
        database,
        invoice_id,
    )

    if invoice.estado == "ANULADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede modificar una factura anulada."
            ),
        )

    for field, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(invoice, field, value)

    database.commit()

    updated = get_invoice_by_id(
        database,
        invoice_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar la factura actualizada."
            ),
        )

    return invoice_to_response(updated)


def register_payment(
    database: Session,
    invoice_id: int,
    payload: PaymentCreate,
) -> InvoiceResponse:
    invoice = get_invoice_or_404(
        database,
        invoice_id,
    )

    if invoice.estado == "ANULADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede pagar una factura anulada."
            ),
        )

    if invoice.estado == "PAGADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La factura ya se encuentra pagada.",
        )

    payment_amount = money(payload.monto)
    pending_balance = money(
        invoice.saldo_pendiente
    )

    if payment_amount > pending_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El pago no puede ser mayor al saldo pendiente."
            ),
        )

    payment = Payment(
        factura_id=invoice_id,
        monto=payment_amount,
        metodo_pago=payload.metodo_pago,
        referencia=payload.referencia,
        observaciones=payload.observaciones,
        estado="APLICADO",
    )

    invoice.total_pagado = money(
        invoice.total_pagado + payment_amount
    )
    invoice.saldo_pendiente = money(
        invoice.total - invoice.total_pagado
    )
    invoice.estado = invoice_status_from_balance(
        invoice.total,
        invoice.total_pagado,
    )

    database.add(payment)
    database.commit()

    updated = get_invoice_by_id(
        database,
        invoice_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar el pago registrado."
            ),
        )

    return invoice_to_response(updated)


def cancel_invoice(
    database: Session,
    invoice_id: int,
    payload: InvoiceCancel,
) -> InvoiceResponse:
    invoice = get_invoice_or_404(
        database,
        invoice_id,
    )

    if money(invoice.total_pagado) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede anular una factura con pagos."
            ),
        )

    if invoice.estado == "ANULADA":
        return invoice_to_response(invoice)

    invoice.estado = "ANULADA"
    invoice.motivo_anulacion = (
        payload.motivo_anulacion
    )
    database.commit()

    updated = get_invoice_by_id(
        database,
        invoice_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar la factura anulada."
            ),
        )

    return invoice_to_response(updated)


def read_billing_summary(
    database: Session,
) -> BillingSummaryResponse:
    invoices = list_all_non_cancelled_invoices(
        database
    )

    total_billed = money(
        sum(
            (
                Decimal(invoice.total)
                for invoice in invoices
            ),
            Decimal("0.00"),
        )
    )
    total_paid = money(
        sum(
            (
                Decimal(invoice.total_pagado)
                for invoice in invoices
            ),
            Decimal("0.00"),
        )
    )
    pending_balance = money(
        sum(
            (
                Decimal(invoice.saldo_pendiente)
                for invoice in invoices
            ),
            Decimal("0.00"),
        )
    )

    return BillingSummaryResponse(
        total_facturado=total_billed,
        total_pagado=total_paid,
        saldo_pendiente=pending_balance,
        facturas_pendientes=sum(
            invoice.estado == "PENDIENTE"
            for invoice in invoices
        ),
        facturas_parciales=sum(
            invoice.estado == "PARCIAL"
            for invoice in invoices
        ),
        facturas_pagadas=sum(
            invoice.estado == "PAGADA"
            for invoice in invoices
        ),
    )
