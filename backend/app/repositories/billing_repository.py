from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.invoice import Invoice
from app.models.payment import Payment


INVOICE_LOAD_OPTIONS = (
    joinedload(Invoice.paciente),
    joinedload(Invoice.consulta),
    selectinload(Invoice.items),
    selectinload(Invoice.pagos),
)


def get_invoice_by_id(
    database: Session,
    invoice_id: int,
) -> Invoice | None:
    statement = (
        select(Invoice)
        .options(*INVOICE_LOAD_OPTIONS)
        .where(Invoice.factura_id == invoice_id)
    )
    return database.scalar(statement)


def get_invoice_by_number(
    database: Session,
    invoice_number: str,
) -> Invoice | None:
    statement = (
        select(Invoice)
        .options(*INVOICE_LOAD_OPTIONS)
        .where(
            func.lower(Invoice.numero_factura)
            == invoice_number.strip().lower()
        )
    )
    return database.scalar(statement)


def list_invoices(
    database: Session,
    patient_id: int | None,
    invoice_status: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Invoice], int]:
    filters = []

    if patient_id is not None:
        filters.append(
            Invoice.paciente_id == patient_id
        )

    if invoice_status is not None:
        filters.append(
            Invoice.estado == invoice_status
        )

    count_statement = select(
        func.count(Invoice.factura_id)
    )
    statement = (
        select(Invoice)
        .options(*INVOICE_LOAD_OPTIONS)
        .order_by(
            Invoice.fecha_emision.desc(),
            Invoice.factura_id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if filters:
        count_statement = count_statement.where(*filters)
        statement = statement.where(*filters)

    total = int(database.scalar(count_statement) or 0)
    invoices = list(
        database.scalars(statement).unique().all()
    )

    return invoices, total


def list_all_non_cancelled_invoices(
    database: Session,
) -> list[Invoice]:
    statement = (
        select(Invoice)
        .where(Invoice.estado != "ANULADA")
    )
    return list(database.scalars(statement).all())
