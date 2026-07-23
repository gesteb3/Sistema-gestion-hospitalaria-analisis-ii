import math
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.lab_order import LabOrder
from app.models.lab_order_item import LabOrderItem
from app.models.lab_result import LabResult
from app.models.lab_test_type import LabTestType
from app.repositories.clinical_repository import (
    get_consultation_by_id,
)
from app.repositories.laboratory_repository import (
    get_lab_order_by_id,
    get_lab_order_item_by_id,
    get_lab_test_type_by_code,
    get_lab_test_type_by_id,
    list_lab_orders,
    list_lab_test_types,
)
from app.schemas.laboratory import (
    LabOrderCreate,
    LabOrderItemResponse,
    LabOrderListResponse,
    LabOrderResponse,
    LabOrderStatusUpdate,
    LabResultCreate,
    LabResultResponse,
    LabTestTypeCreate,
    LabTestTypeResponse,
    LabTestTypeUpdate,
)
from app.utils.laboratory import order_is_complete


def test_type_to_response(
    test_type: LabTestType,
) -> LabTestTypeResponse:
    return LabTestTypeResponse(
        tipo_examen_id=test_type.tipo_examen_id,
        codigo=test_type.codigo,
        nombre=test_type.nombre,
        descripcion=test_type.descripcion,
        muestra_requerida=test_type.muestra_requerida,
        tiempo_estimado_horas=(
            test_type.tiempo_estimado_horas
        ),
        precio=Decimal(test_type.precio),
        activo=test_type.esta_activo,
        fecha_creacion=test_type.fecha_creacion,
    )


def order_to_response(
    order: LabOrder,
) -> LabOrderResponse:
    consultation = order.consulta
    appointment = consultation.cita
    patient = appointment.paciente
    doctor = consultation.medico

    items = [
        LabOrderItemResponse(
            detalle_orden_id=item.detalle_orden_id,
            tipo_examen_id=item.tipo_examen_id,
            codigo_examen=item.tipo_examen.codigo,
            nombre_examen=item.tipo_examen.nombre,
            muestra_requerida=(
                item.tipo_examen.muestra_requerida
            ),
            precio=Decimal(item.tipo_examen.precio),
            observaciones=item.observaciones,
            estado=item.estado,
            fecha_procesamiento=item.fecha_procesamiento,
            resultado=(
                LabResultResponse(
                    resultado_id=item.resultado.resultado_id,
                    resultado=item.resultado.resultado,
                    valores_referencia=(
                        item.resultado.valores_referencia
                    ),
                    interpretacion=(
                        item.resultado.interpretacion
                    ),
                    archivo_url=item.resultado.archivo_url,
                    fecha_resultado=(
                        item.resultado.fecha_resultado
                    ),
                )
                if item.resultado is not None
                else None
            ),
        )
        for item in sorted(
            order.items,
            key=lambda record: record.detalle_orden_id,
        )
    ]

    total = sum(
        (
            Decimal(item.tipo_examen.precio)
            for item in order.items
        ),
        Decimal("0.00"),
    )

    return LabOrderResponse(
        orden_laboratorio_id=(
            order.orden_laboratorio_id
        ),
        consulta_id=order.consulta_id,
        paciente_id=patient.paciente_id,
        numero_expediente=(
            patient.numero_expediente or ""
        ),
        paciente_nombre=(
            f"{patient.nombres} {patient.apellidos}"
        ),
        medico_id=doctor.medico_id,
        medico_nombre=(
            f"{doctor.nombres} {doctor.apellidos}"
        ),
        indicaciones=order.indicaciones,
        prioridad=order.prioridad,
        estado=order.estado,
        motivo_cancelacion=order.motivo_cancelacion,
        items=items,
        total_estimado=total,
        fecha_solicitud=order.fecha_solicitud,
        fecha_completada=order.fecha_completada,
    )


def create_test_type(
    database: Session,
    payload: LabTestTypeCreate,
) -> LabTestTypeResponse:
    if get_lab_test_type_by_code(
        database,
        payload.codigo,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El código del examen ya está registrado."
            ),
        )

    test_type = LabTestType(
        codigo=payload.codigo,
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        muestra_requerida=payload.muestra_requerida,
        tiempo_estimado_horas=(
            payload.tiempo_estimado_horas
        ),
        precio=payload.precio,
        estado=1,
    )

    database.add(test_type)
    database.commit()
    database.refresh(test_type)

    return test_type_to_response(test_type)


def read_test_types(
    database: Session,
    include_inactive: bool,
) -> list[LabTestTypeResponse]:
    return [
        test_type_to_response(test_type)
        for test_type in list_lab_test_types(
            database,
            include_inactive,
        )
    ]


def update_test_type(
    database: Session,
    test_type_id: int,
    payload: LabTestTypeUpdate,
) -> LabTestTypeResponse:
    test_type = get_lab_test_type_by_id(
        database,
        test_type_id,
    )

    if test_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de examen no encontrado.",
        )

    for field, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(test_type, field, value)

    database.commit()
    database.refresh(test_type)

    return test_type_to_response(test_type)


def create_lab_order(
    database: Session,
    payload: LabOrderCreate,
) -> LabOrderResponse:
    consultation = get_consultation_by_id(
        database,
        payload.consulta_id,
    )

    if consultation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta clínica no encontrada.",
        )

    test_types: dict[int, LabTestType] = {}

    for item in payload.items:
        test_type = get_lab_test_type_by_id(
            database,
            item.tipo_examen_id,
        )

        if test_type is None or not test_type.esta_activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"El examen {item.tipo_examen_id} "
                    "no existe o está inactivo."
                ),
            )

        test_types[item.tipo_examen_id] = test_type

    order = LabOrder(
        consulta_id=payload.consulta_id,
        indicaciones=payload.indicaciones,
        prioridad=payload.prioridad,
        estado="SOLICITADA",
    )

    for item in payload.items:
        order.items.append(
            LabOrderItem(
                tipo_examen_id=item.tipo_examen_id,
                observaciones=item.observaciones,
                estado="PENDIENTE",
            )
        )

    database.add(order)

    try:
        database.commit()
        database.refresh(order)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No fue posible registrar la orden de laboratorio."
            ),
        ) from exc

    stored = get_lab_order_by_id(
        database,
        order.orden_laboratorio_id,
    )

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "La orden fue creada, pero no pudo recuperarse."
            ),
        )

    return order_to_response(stored)


def get_order_or_404(
    database: Session,
    order_id: int,
) -> LabOrder:
    order = get_lab_order_by_id(
        database,
        order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de laboratorio no encontrada.",
        )

    return order


def read_lab_order(
    database: Session,
    order_id: int,
) -> LabOrderResponse:
    return order_to_response(
        get_order_or_404(
            database,
            order_id,
        )
    )


def read_lab_orders(
    database: Session,
    patient_id: int | None,
    order_status: str | None,
    page: int,
    page_size: int,
) -> LabOrderListResponse:
    normalized_status = (
        order_status.strip().upper()
        if order_status
        else None
    )

    orders, total = list_lab_orders(
        database=database,
        patient_id=patient_id,
        order_status=normalized_status,
        page=page,
        page_size=page_size,
    )

    return LabOrderListResponse(
        items=[
            order_to_response(order)
            for order in orders
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(
            math.ceil(total / page_size)
            if total > 0
            else 0
        ),
    )


def update_order_status(
    database: Session,
    order_id: int,
    payload: LabOrderStatusUpdate,
) -> LabOrderResponse:
    order = get_order_or_404(
        database,
        order_id,
    )

    if order.estado in {
        "COMPLETADA",
        "CANCELADA",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede modificar una orden finalizada."
            ),
        )

    if payload.estado == "COMPLETADA":
        if not order_is_complete(
            [item.estado for item in order.items]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Todos los exámenes deben tener resultado "
                    "antes de completar la orden."
                ),
            )

        order.fecha_completada = (
            datetime.now(timezone.utc).replace(tzinfo=None)
        )

    order.estado = payload.estado
    order.motivo_cancelacion = (
        payload.motivo_cancelacion
        if payload.estado == "CANCELADA"
        else None
    )

    if payload.estado == "EN_PROCESO":
        for item in order.items:
            if item.estado == "PENDIENTE":
                item.estado = "PROCESANDO"

    database.commit()

    updated = get_lab_order_by_id(
        database,
        order_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar la orden actualizada."
            ),
        )

    return order_to_response(updated)


def register_result(
    database: Session,
    order_id: int,
    item_id: int,
    payload: LabResultCreate,
) -> LabOrderResponse:
    order = get_order_or_404(
        database,
        order_id,
    )

    if order.estado == "CANCELADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se pueden registrar resultados "
                "en una orden cancelada."
            ),
        )

    item = get_lab_order_item_by_id(
        database,
        item_id,
    )

    if (
        item is None
        or item.orden_laboratorio_id != order_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Examen no encontrado dentro de la orden."
            ),
        )

    if item.resultado is None:
        item.resultado = LabResult(
            resultado=payload.resultado,
            valores_referencia=(
                payload.valores_referencia
            ),
            interpretacion=payload.interpretacion,
            archivo_url=payload.archivo_url,
        )
    else:
        item.resultado.resultado = payload.resultado
        item.resultado.valores_referencia = (
            payload.valores_referencia
        )
        item.resultado.interpretacion = (
            payload.interpretacion
        )
        item.resultado.archivo_url = payload.archivo_url

    item.estado = "COMPLETADO"
    item.fecha_procesamiento = (
        datetime.now(timezone.utc).replace(tzinfo=None)
    )

    if order.estado == "SOLICITADA":
        order.estado = "EN_PROCESO"

    if order_is_complete(
        [
            (
                "COMPLETADO"
                if record.detalle_orden_id == item_id
                else record.estado
            )
            for record in order.items
        ]
    ):
        order.estado = "COMPLETADA"
        order.fecha_completada = (
            datetime.now(timezone.utc).replace(tzinfo=None)
        )

    database.commit()

    updated = get_lab_order_by_id(
        database,
        order_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar el resultado."
            ),
        )

    return order_to_response(updated)
