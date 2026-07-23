from app.utils.laboratory import order_is_complete


def test_order_is_complete() -> None:
    assert order_is_complete(
        ["COMPLETADO", "COMPLETADO"]
    )


def test_order_is_not_complete() -> None:
    assert not order_is_complete(
        ["COMPLETADO", "PROCESANDO"]
    )


def test_empty_order_is_not_complete() -> None:
    assert not order_is_complete([])
