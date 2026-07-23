from datetime import date

from app.utils.schedules import minutes_to_time, time_to_minutes


ACTIVE_APPOINTMENT_STATUSES = {
    "PROGRAMADA",
    "CONFIRMADA",
}

FINAL_APPOINTMENT_STATUSES = {
    "COMPLETADA",
    "CANCELADA",
    "NO_ASISTIO",
}

ALLOWED_APPOINTMENT_STATUSES = (
    ACTIVE_APPOINTMENT_STATUSES
    | FINAL_APPOINTMENT_STATUSES
)

STATUS_TRANSITIONS = {
    "PROGRAMADA": {
        "CONFIRMADA",
        "COMPLETADA",
        "CANCELADA",
        "NO_ASISTIO",
    },
    "CONFIRMADA": {
        "COMPLETADA",
        "CANCELADA",
        "NO_ASISTIO",
    },
    "COMPLETADA": set(),
    "CANCELADA": set(),
    "NO_ASISTIO": set(),
}


def appointment_end_time(
    start_time: str,
    duration_minutes: int,
) -> str:
    end_minutes = (
        time_to_minutes(start_time)
        + duration_minutes
    )
    return minutes_to_time(end_minutes)


def appointment_overlaps(
    first_start: str,
    first_duration: int,
    second_start: str,
    second_duration: int,
) -> bool:
    first_start_minutes = time_to_minutes(first_start)
    first_end_minutes = first_start_minutes + first_duration
    second_start_minutes = time_to_minutes(second_start)
    second_end_minutes = second_start_minutes + second_duration

    return (
        first_start_minutes < second_end_minutes
        and second_start_minutes < first_end_minutes
    )


def appointment_day_number(
    appointment_date: date,
) -> int:
    return appointment_date.isoweekday()


def can_transition_status(
    current_status: str,
    new_status: str,
) -> bool:
    if current_status == new_status:
        return True

    return new_status in STATUS_TRANSITIONS.get(
        current_status,
        set(),
    )


def generate_time_slots(
    start_time: str,
    end_time: str,
    duration_minutes: int,
) -> list[str]:
    start_minutes = time_to_minutes(start_time)
    end_minutes = time_to_minutes(end_time)

    slots: list[str] = []
    current = start_minutes

    while current + duration_minutes <= end_minutes:
        slots.append(minutes_to_time(current))
        current += duration_minutes

    return slots
