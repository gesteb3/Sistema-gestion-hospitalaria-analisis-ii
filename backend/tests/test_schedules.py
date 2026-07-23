import pytest

from app.utils.schedules import (
    day_name,
    schedules_overlap,
    validate_time_format,
)


def test_schedule_overlap() -> None:
    assert schedules_overlap(
        "08:00",
        "12:00",
        "11:30",
        "13:00",
    )
    assert not schedules_overlap(
        "08:00",
        "12:00",
        "12:00",
        "14:00",
    )


def test_validate_time_format() -> None:
    assert validate_time_format("08:30") == "08:30"

    with pytest.raises(ValueError):
        validate_time_format("25:00")


def test_day_name() -> None:
    assert day_name(1) == "LUNES"
    assert day_name(7) == "DOMINGO"
