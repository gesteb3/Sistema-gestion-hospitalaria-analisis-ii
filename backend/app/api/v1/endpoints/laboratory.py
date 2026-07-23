from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import (
    DatabaseDependency,
    LaboratoryOrderWriterDependency,
    LaboratoryProcessorDependency,
    LaboratoryReaderDependency,
)
from app.schemas.laboratory import (
    LabOrderCreate,
    LabOrderListResponse,
    LabOrderResponse,
    LabOrderStatusUpdate,
    LabResultCreate,
    LabTestTypeCreate,
    LabTestTypeResponse,
    LabTestTypeUpdate,
)
from app.services.laboratory_service import (
    create_lab_order,
    create_test_type,
    read_lab_order,
    read_lab_orders,
    read_test_types,
    register_result,
    update_order_status,
    update_test_type,
)


test_type_router = APIRouter(
    prefix="/lab-tests",
    tags=["Tipos de examen"],
)

lab_order_router = APIRouter(
    prefix="/lab-orders",
    tags=["Laboratorio"],
)


@test_type_router.get(
    "",
    response_model=list[LabTestTypeResponse],
)
def list_test_types(
    database: DatabaseDependency,
    _: LaboratoryReaderDependency,
    include_inactive: bool = False,
) -> list[LabTestTypeResponse]:
    return read_test_types(
        database,
        include_inactive,
    )


@test_type_router.post(
    "",
    response_model=LabTestTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_test_type(
    payload: LabTestTypeCreate,
    database: DatabaseDependency,
    _: LaboratoryProcessorDependency,
) -> LabTestTypeResponse:
    return create_test_type(
        database,
        payload,
    )


@test_type_router.put(
    "/{test_type_id}",
    response_model=LabTestTypeResponse,
)
def modify_test_type(
    test_type_id: int,
    payload: LabTestTypeUpdate,
    database: DatabaseDependency,
    _: LaboratoryProcessorDependency,
) -> LabTestTypeResponse:
    return update_test_type(
        database,
        test_type_id,
        payload,
    )


@lab_order_router.post(
    "",
    response_model=LabOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_lab_order(
    payload: LabOrderCreate,
    database: DatabaseDependency,
    _: LaboratoryOrderWriterDependency,
) -> LabOrderResponse:
    return create_lab_order(
        database,
        payload,
    )


@lab_order_router.get(
    "",
    response_model=LabOrderListResponse,
)
def list_registered_lab_orders(
    database: DatabaseDependency,
    _: LaboratoryReaderDependency,
    patient_id: int | None = None,
    order_status: Annotated[
        str | None,
        Query(alias="status"),
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> LabOrderListResponse:
    return read_lab_orders(
        database=database,
        patient_id=patient_id,
        order_status=order_status,
        page=page,
        page_size=page_size,
    )


@lab_order_router.get(
    "/{order_id}",
    response_model=LabOrderResponse,
)
def get_registered_lab_order(
    order_id: int,
    database: DatabaseDependency,
    _: LaboratoryReaderDependency,
) -> LabOrderResponse:
    return read_lab_order(
        database,
        order_id,
    )


@lab_order_router.patch(
    "/{order_id}/status",
    response_model=LabOrderResponse,
)
def change_lab_order_status(
    order_id: int,
    payload: LabOrderStatusUpdate,
    database: DatabaseDependency,
    _: LaboratoryProcessorDependency,
) -> LabOrderResponse:
    return update_order_status(
        database,
        order_id,
        payload,
    )


@lab_order_router.post(
    "/{order_id}/items/{item_id}/result",
    response_model=LabOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_lab_result(
    order_id: int,
    item_id: int,
    payload: LabResultCreate,
    database: DatabaseDependency,
    _: LaboratoryProcessorDependency,
) -> LabOrderResponse:
    return register_result(
        database,
        order_id,
        item_id,
        payload,
    )
