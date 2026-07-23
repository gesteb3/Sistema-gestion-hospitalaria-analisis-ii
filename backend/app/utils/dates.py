from datetime import date


def calculate_age(
    birth_date: date,
    reference_date: date | None = None,
) -> int:
    today = reference_date or date.today()

    years = today.year - birth_date.year
    birthday_has_not_occurred = (
        today.month,
        today.day,
    ) < (
        birth_date.month,
        birth_date.day,
    )

    return years - int(birthday_has_not_occurred)


def is_minor(
    birth_date: date,
    reference_date: date | None = None,
) -> bool:
    return calculate_age(
        birth_date,
        reference_date,
    ) < 18


def build_record_number(
    patient_id: int,
    creation_date: date | None = None,
) -> str:
    year = (creation_date or date.today()).year
    return f"EXP-{year}-{patient_id:06d}"
