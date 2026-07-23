from decimal import Decimal

from app.utils.billing import (
    build_invoice_number,
    calculate_invoice_totals,
    calculate_line_subtotal,
    invoice_status_from_balance,
)


def test_calculate_line_subtotal() -> None:
    assert calculate_line_subtotal(
        2,
        Decimal("75.00"),
    ) == Decimal("150.00")


def test_calculate_invoice_totals() -> None:
    subtotal, total = calculate_invoice_totals(
        [
            Decimal("100.00"),
            Decimal("50.00"),
        ],
        Decimal("10.00"),
    )
    assert subtotal == Decimal("150.00")
    assert total == Decimal("140.00")


def test_invoice_status_from_balance() -> None:
    assert invoice_status_from_balance(
        Decimal("100.00"),
        Decimal("0.00"),
    ) == "PENDIENTE"

    assert invoice_status_from_balance(
        Decimal("100.00"),
        Decimal("40.00"),
    ) == "PARCIAL"

    assert invoice_status_from_balance(
        Decimal("100.00"),
        Decimal("100.00"),
    ) == "PAGADA"


def test_build_invoice_number() -> None:
    assert build_invoice_number(
        12,
        2026,
    ) == "FAC-2026-000012"
