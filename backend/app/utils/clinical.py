def calculate_bmi(
    weight_kg: float | None,
    height_cm: float | None,
) -> float | None:
    if weight_kg is None or height_cm is None:
        return None

    if weight_kg <= 0 or height_cm <= 0:
        return None

    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def blood_pressure_text(
    systolic: int | None,
    diastolic: int | None,
) -> str | None:
    if systolic is None or diastolic is None:
        return None

    return f"{systolic}/{diastolic}"
