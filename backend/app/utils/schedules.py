import re


TIME_PATTERN = re.compile(
    r"^(?:[01]\d|2[0-3]):[0-5]\d$"
)

DAY_NAMES = {
    1: "LUNES",
    2: "MARTES",
    3: "MIÉRCOLES",
    4: "JUEVES",
    5: "VIERNES",
    6: "SÁBADO",
    7: "DOMINGO",
}


def validate_time_format(value: str) -> str:
    normalized = value.strip()

    if not TIME_PATTERN.fullmatch(normalized):
        raise ValueError(
            "La hora debe utilizar el formato HH:MM de 24 horas."
        )

    return normalized


def schedules_overlap(
    first_start: str,
    first_end: str,
    second_start: str,
    second_end: str,
) -> bool:
    return (
        first_start < second_end
        and second_start < first_end
    )


def day_name(day_number: int) -> str:
    return DAY_NAMES[day_number]
