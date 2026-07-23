PRESCRIPTION_STATUSES = {
    "EMITIDA",
    "DISPENSADA",
    "ANULADA",
}

MOVEMENT_TYPES = {
    "ENTRADA",
    "SALIDA",
    "AJUSTE",
}


def calculate_new_stock(
    current_stock: int,
    movement_type: str,
    quantity: int,
) -> int:
    normalized = movement_type.strip().upper()

    if normalized == "ENTRADA":
        return current_stock + quantity

    if normalized == "SALIDA":
        return current_stock - quantity

    if normalized == "AJUSTE":
        return quantity

    raise ValueError("Tipo de movimiento no válido.")


def has_sufficient_stock(
    current_stock: int,
    requested_quantity: int,
) -> bool:
    return current_stock >= requested_quantity
