from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import (
    BillingReaderDependency,
    BillingWriterDependency,
    DatabaseDependency,
)
from app.schemas.billing import (
    BillingSummaryResponse,
    InvoiceCancel,
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceUpdate,
    PaymentCreate,
)
from app.services.billing_service import (
    cancel_invoice,
    create_invoice,
    read_billing_summary,
    read_invoice,
    read_invoices,
    register_payment,
    update_invoice,
)


router = APIRouter(
    prefix="/billing",
    tags=["Facturación"],
)


@router.get(
    "/summary",
    response_model=BillingSummaryResponse,
)
def get_billing_summary(
    database: DatabaseDependency,
    _: BillingReaderDependency,
) -> BillingSummaryResponse:
    return read_billing_summary(database)


@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_invoice(
    payload: InvoiceCreate,
    database: DatabaseDependency,
    _: BillingWriterDependency,
) -> InvoiceResponse:
    return create_invoice(
        database,
        payload,
    )


@router.get(
    "/invoices",
    response_model=InvoiceListResponse,
)
def list_registered_invoices(
    database: DatabaseDependency,
    _: BillingReaderDependency,
    patient_id: int | None = None,
    invoice_status: Annotated[
        str | None,
        Query(alias="status"),
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> InvoiceListResponse:
    return read_invoices(
        database=database,
        patient_id=patient_id,
        invoice_status=invoice_status,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
)
def get_registered_invoice(
    invoice_id: int,
    database: DatabaseDependency,
    _: BillingReaderDependency,
) -> InvoiceResponse:
    return read_invoice(
        database,
        invoice_id,
    )


@router.put(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
)
def modify_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    database: DatabaseDependency,
    _: BillingWriterDependency,
) -> InvoiceResponse:
    return update_invoice(
        database,
        invoice_id,
        payload,
    )


@router.post(
    "/invoices/{invoice_id}/payments",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_invoice_payment(
    invoice_id: int,
    payload: PaymentCreate,
    database: DatabaseDependency,
    _: BillingWriterDependency,
) -> InvoiceResponse:
    return register_payment(
        database,
        invoice_id,
        payload,
    )


@router.patch(
    "/invoices/{invoice_id}/cancel",
    response_model=InvoiceResponse,
)
def cancel_registered_invoice(
    invoice_id: int,
    payload: InvoiceCancel,
    database: DatabaseDependency,
    _: BillingWriterDependency,
) -> InvoiceResponse:
    return cancel_invoice(
        database,
        invoice_id,
        payload,
    )
