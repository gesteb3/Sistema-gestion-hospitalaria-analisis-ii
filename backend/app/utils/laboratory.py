LAB_ORDER_STATUSES = {
    "SOLICITADA",
    "EN_PROCESO",
    "COMPLETADA",
    "CANCELADA",
}

LAB_ITEM_STATUSES = {
    "PENDIENTE",
    "PROCESANDO",
    "COMPLETADO",
}

LAB_PRIORITIES = {
    "NORMAL",
    "URGENTE",
}


def order_is_complete(
    item_statuses: list[str],
) -> bool:
    return (
        bool(item_statuses)
        and all(
            status == "COMPLETADO"
            for status in item_statuses
        )
    )
