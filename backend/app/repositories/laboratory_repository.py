from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.consultation import Consultation
from app.models.lab_order import LabOrder
from app.models.lab_order_item import LabOrderItem
from app.models.lab_test_type import LabTestType


LAB_ORDER_LOAD_OPTIONS = (
    joinedload(LabOrder.consulta)
    .joinedload(Consultation.cita),
    joinedload(LabOrder.consulta)
    .joinedload(Consultation.medico),
    selectinload(LabOrder.items)
    .joinedload(LabOrderItem.tipo_examen),
    selectinload(LabOrder.items)
    .selectinload(LabOrderItem.resultado),
)


def get_lab_test_type_by_id(
    database: Session,
    test_type_id: int,
) -> LabTestType | None:
    return database.get(
        LabTestType,
        test_type_id,
    )


def get_lab_test_type_by_code(
    database: Session,
    code: str,
) -> LabTestType | None:
    statement = select(LabTestType).where(
        func.lower(LabTestType.codigo)
        == code.strip().lower()
    )
    return database.scalar(statement)


def list_lab_test_types(
    database: Session,
    include_inactive: bool,
) -> list[LabTestType]:
    statement = select(LabTestType).order_by(
        LabTestType.nombre
    )

    if not include_inactive:
        statement = statement.where(
            LabTestType.estado == 1
        )

    return list(database.scalars(statement).all())


def get_lab_order_by_id(
    database: Session,
    order_id: int,
) -> LabOrder | None:
    statement = (
        select(LabOrder)
        .options(*LAB_ORDER_LOAD_OPTIONS)
        .where(
            LabOrder.orden_laboratorio_id == order_id
        )
    )
    return database.scalar(statement)


def get_lab_order_item_by_id(
    database: Session,
    item_id: int,
) -> LabOrderItem | None:
    statement = (
        select(LabOrderItem)
        .options(
            joinedload(LabOrderItem.tipo_examen),
            selectinload(LabOrderItem.resultado),
        )
        .where(
            LabOrderItem.detalle_orden_id == item_id
        )
    )
    return database.scalar(statement)


def list_lab_orders(
    database: Session,
    patient_id: int | None,
    order_status: str | None,
    page: int,
    page_size: int,
) -> tuple[list[LabOrder], int]:
    filters = []

    if patient_id is not None:
        filters.append(
            LabOrder.consulta.has(
                Consultation.cita.has(
                    paciente_id=patient_id
                )
            )
        )

    if order_status is not None:
        filters.append(
            LabOrder.estado == order_status
        )

    count_statement = select(
        func.count(LabOrder.orden_laboratorio_id)
    )
    statement = (
        select(LabOrder)
        .options(*LAB_ORDER_LOAD_OPTIONS)
        .order_by(
            LabOrder.fecha_solicitud.desc(),
            LabOrder.orden_laboratorio_id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if filters:
        count_statement = count_statement.where(*filters)
        statement = statement.where(*filters)

    total = int(database.scalar(count_statement) or 0)
    orders = list(
        database.scalars(statement).unique().all()
    )

    return orders, total
