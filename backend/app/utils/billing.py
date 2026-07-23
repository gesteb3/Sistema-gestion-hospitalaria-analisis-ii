from decimal import Decimal, ROUND_HALF_UP


INVOICE_STATUSES = {
    "PENDIENTE",
    "PARCIAL",
    "PAGADA",
    "ANULADA",
}

PAYMENT_METHODS = {
    "EFECTIVO",
    "TARJETA",
    "TRANSFERENCIA",
    "CHEQUE",
}


def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def calculate_line_subtotal(
    quantity: int,
    unit_price: Decimal,
) -> Decimal:
    return money(
        Decimal(quantity) * money(unit_price)
    )


def calculate_invoice_totals(
    subtotals: list[Decimal],
    discount: Decimal,
) -> tuple[Decimal, Decimal]:
    subtotal = money(sum(subtotals, Decimal("0.00")))
    normalized_discount = money(discount)
    total = money(subtotal - normalized_discount)
    return subtotal, total


def invoice_status_from_balance(
    total: Decimal,
    total_paid: Decimal,
) -> str:
    total = money(total)
    total_paid = money(total_paid)

    if total_paid <= 0:
        return "PENDIENTE"

    if total_paid < total:
        return "PARCIAL"

    return "PAGADA"


def build_invoice_number(
    invoice_id: int,
    year: int,
) -> str:
    return f"FAC-{year}-{invoice_id:06d}"
