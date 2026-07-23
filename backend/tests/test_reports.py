from decimal import Decimal

from app.utils.billing import money


def test_report_money_rounding() -> None:
    assert money(
        Decimal("100.125")
    ) == Decimal("100.13")


def test_zero_report_money() -> None:
    assert money(0) == Decimal("0.00")
