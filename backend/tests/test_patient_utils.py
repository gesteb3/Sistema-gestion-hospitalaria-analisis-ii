from datetime import date

from app.utils.dates import (
    build_record_number,
    calculate_age,
    is_minor,
)


def test_calculate_age_before_birthday() -> None:
    age = calculate_age(
        date(2010, 12, 20),
        date(2026, 7, 23),
    )
    assert age == 15
    assert is_minor(
        date(2010, 12, 20),
        date(2026, 7, 23),
    )


def test_calculate_age_after_birthday() -> None:
    age = calculate_age(
        date(2000, 1, 10),
        date(2026, 7, 23),
    )
    assert age == 26
    assert not is_minor(
        date(2000, 1, 10),
        date(2026, 7, 23),
    )


def test_build_record_number() -> None:
    record_number = build_record_number(
        patient_id=25,
        creation_date=date(2026, 7, 23),
    )
    assert record_number == "EXP-2026-000025"
