from app.utils.clinical import (
    blood_pressure_text,
    calculate_bmi,
)


def test_calculate_bmi() -> None:
    assert calculate_bmi(
        70,
        175,
    ) == 22.86


def test_calculate_bmi_without_values() -> None:
    assert calculate_bmi(None, 175) is None
    assert calculate_bmi(70, None) is None


def test_blood_pressure_text() -> None:
    assert blood_pressure_text(
        120,
        80,
    ) == "120/80"
    assert blood_pressure_text(
        None,
        80,
    ) is None
