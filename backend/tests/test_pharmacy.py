import pytest

from app.utils.pharmacy import (
    calculate_new_stock,
    has_sufficient_stock,
)


def test_calculate_entry_stock() -> None:
    assert calculate_new_stock(
        10,
        "ENTRADA",
        5,
    ) == 15


def test_calculate_exit_stock() -> None:
    assert calculate_new_stock(
        10,
        "SALIDA",
        4,
    ) == 6


def test_calculate_adjustment_stock() -> None:
    assert calculate_new_stock(
        10,
        "AJUSTE",
        7,
    ) == 7


def test_invalid_movement_type() -> None:
    with pytest.raises(ValueError):
        calculate_new_stock(
            10,
            "DESCONOCIDO",
            2,
        )


def test_sufficient_stock() -> None:
    assert has_sufficient_stock(10, 10)
    assert not has_sufficient_stock(5, 6)
