from datetime import date

from app.utils.appointments import (
    appointment_day_number,
    appointment_end_time,
    appointment_overlaps,
    can_transition_status,
    generate_time_slots,
)


def test_appointment_end_time() -> None:
    assert appointment_end_time(
        "08:30",
        30,
    ) == "09:00"


def test_appointment_overlap() -> None:
    assert appointment_overlaps(
        "08:00",
        30,
        "08:15",
        30,
    )
    assert not appointment_overlaps(
        "08:00",
        30,
        "08:30",
        30,
    )


def test_generate_time_slots() -> None:
    assert generate_time_slots(
        "08:00",
        "10:00",
        30,
    ) == [
        "08:00",
        "08:30",
        "09:00",
        "09:30",
    ]


def test_status_transitions() -> None:
    assert can_transition_status(
        "PROGRAMADA",
        "CONFIRMADA",
    )
    assert can_transition_status(
        "CONFIRMADA",
        "COMPLETADA",
    )
    assert not can_transition_status(
        "COMPLETADA",
        "PROGRAMADA",
    )


def test_appointment_day_number() -> None:
    assert appointment_day_number(
        date(2026, 7, 27)
    ) == 1
