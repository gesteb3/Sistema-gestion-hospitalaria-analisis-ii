import math
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.inventory_movement import InventoryMovement
from app.models.medication import Medication
from app.models.prescription import Prescription
from app.models.prescription_item import PrescriptionItem
from app.repositories.clinical_repository import (
    get_consultation_by_id,
)
from app.repositories.pharmacy_repository import (
    get_medication_by_code,
    get_medication_by_id,
    get_prescription_by_consultation_id,
    get_prescription_by_id,
    list_medications,
    list_prescriptions,
)
from app.schemas.pharmacy import (
    InventoryMovementResponse,
    MedicationCreate,
    MedicationListResponse,
    MedicationResponse,
    MedicationUpdate,
    PrescriptionCancel,
    PrescriptionCreate,
    PrescriptionItemResponse,
    PrescriptionListResponse,
    PrescriptionResponse,
    StockMovementCreate,
)
from app.utils.pharmacy import (
    calculate_new_stock,
    has_sufficient_stock,
)


def medication_to_response(
    medication: Medication,
) -> MedicationResponse:
    return MedicationResponse(
        medicamento_id=medication.medicamento_id,
        codigo=medication.codigo,
        nombre=medication.nombre,
        principio_activo=medication.principio_activo,
        concentracion=medication.concentracion,
        presentacion=medication.presentacion,
        unidad=medication.unidad,
        stock_actual=medication.stock_actual,
        stock_minimo=medication.stock_minimo,
        stock_bajo=medication.stock_bajo,
        precio_unitario=Decimal(
            medication.precio_unitario
        ),
        activo=medication.esta_activo,
        fecha_creacion=medication.fecha_creacion,
        fecha_actualizacion=medication.fecha_actualizacion,
    )


def prescription_to_response(
    prescription: Prescription,
) -> PrescriptionResponse:
    consultation = prescription.consulta
    appointment = consultation.cita
    patient = appointment.paciente
    doctor = consultation.medico

    return PrescriptionResponse(
        receta_id=prescription.receta_id,
        consulta_id=prescription.consulta_id,
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
        indicaciones_generales=(
            prescription.indicaciones_generales
        ),
        estado=prescription.estado,
        motivo_anulacion=prescription.motivo_anulacion,
        items=[
            PrescriptionItemResponse(
                detalle_receta_id=item.detalle_receta_id,
                medicamento_id=item.medicamento_id,
                medicamento_codigo=(
                    item.medicamento.codigo
                ),
                medicamento_nombre=(
                    item.medicamento.nombre
                ),
                dosis=item.dosis,
                via_administracion=(
                    item.via_administracion
                ),
                frecuencia=item.frecuencia,
                duracion=item.duracion,
                cantidad=item.cantidad,
                cantidad_dispensada=(
                    item.cantidad_dispensada
                ),
                indicaciones=item.indicaciones,
            )
            for item in sorted(
                prescription.items,
                key=lambda record: (
                    record.detalle_receta_id
                ),
            )
        ],
        fecha_emision=prescription.fecha_emision,
        fecha_dispensacion=(
            prescription.fecha_dispensacion
        ),
    )


def get_medication_or_404(
    database: Session,
    medication_id: int,
) -> Medication:
    medication = get_medication_by_id(
        database,
        medication_id,
    )

    if medication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicamento no encontrado.",
        )

    return medication


def create_medication(
    database: Session,
    payload: MedicationCreate,
) -> MedicationResponse:
    if get_medication_by_code(database, payload.codigo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El código del medicamento ya está registrado."
            ),
        )

    medication = Medication(
        codigo=payload.codigo,
        nombre=payload.nombre,
        principio_activo=payload.principio_activo,
        concentracion=payload.concentracion,
        presentacion=payload.presentacion,
        unidad=payload.unidad,
        stock_actual=payload.stock_actual,
        stock_minimo=payload.stock_minimo,
        precio_unitario=payload.precio_unitario,
        estado=1,
    )

    database.add(medication)

    try:
        database.flush()

        if payload.stock_actual > 0:
            database.add(
                InventoryMovement(
                    medicamento_id=medication.medicamento_id,
                    tipo="ENTRADA",
                    cantidad=payload.stock_actual,
                    stock_anterior=0,
                    stock_nuevo=payload.stock_actual,
                    motivo="Inventario inicial",
                )
            )

        database.commit()
        database.refresh(medication)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar el medicamento.",
        ) from exc

    return medication_to_response(medication)


def read_medications(
    database: Session,
    search: str | None,
    low_stock: bool | None,
    include_inactive: bool,
    page: int,
    page_size: int,
) -> MedicationListResponse:
    medications, total = list_medications(
        database=database,
        search=search,
        low_stock=low_stock,
        include_inactive=include_inactive,
        page=page,
        page_size=page_size,
    )

    return MedicationListResponse(
        items=[
            medication_to_response(medication)
            for medication in medications
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


def read_medication(
    database: Session,
    medication_id: int,
) -> MedicationResponse:
    return medication_to_response(
        get_medication_or_404(
            database,
            medication_id,
        )
    )


def update_medication(
    database: Session,
    medication_id: int,
    payload: MedicationUpdate,
) -> MedicationResponse:
    medication = get_medication_or_404(
        database,
        medication_id,
    )

    for field, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(medication, field, value)

    database.commit()
    database.refresh(medication)

    return medication_to_response(medication)


def register_stock_movement(
    database: Session,
    medication_id: int,
    payload: StockMovementCreate,
) -> InventoryMovementResponse:
    medication = get_medication_or_404(
        database,
        medication_id,
    )

    previous_stock = medication.stock_actual
    new_stock = calculate_new_stock(
        previous_stock,
        payload.tipo,
        payload.cantidad,
    )

    medication.stock_actual = new_stock

    movement = InventoryMovement(
        medicamento_id=medication_id,
        tipo=payload.tipo,
        cantidad=payload.cantidad,
        stock_anterior=previous_stock,
        stock_nuevo=new_stock,
        motivo=payload.motivo,
    )

    database.add(movement)
    database.commit()
    database.refresh(movement)

    return InventoryMovementResponse(
        movimiento_id=movement.movimiento_id,
        medicamento_id=medication.medicamento_id,
        medicamento_nombre=medication.nombre,
        receta_id=None,
        tipo=movement.tipo,
        cantidad=movement.cantidad,
        stock_anterior=movement.stock_anterior,
        stock_nuevo=movement.stock_nuevo,
        motivo=movement.motivo,
        fecha_movimiento=movement.fecha_movimiento,
    )


def create_prescription(
    database: Session,
    payload: PrescriptionCreate,
) -> PrescriptionResponse:
    consultation = get_consultation_by_id(
        database,
        payload.consulta_id,
    )

    if consultation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta clínica no encontrada.",
        )

    if get_prescription_by_consultation_id(
        database,
        payload.consulta_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "La consulta ya tiene una receta registrada."
            ),
        )

    medication_ids = [
        item.medicamento_id
        for item in payload.items
    ]
    medications: dict[int, Medication] = {}

    for medication_id in medication_ids:
        medication = get_medication_by_id(
            database,
            medication_id,
        )

        if medication is None or not medication.esta_activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"El medicamento {medication_id} "
                    "no existe o está inactivo."
                ),
            )

        medications[medication_id] = medication

    prescription = Prescription(
        consulta_id=payload.consulta_id,
        indicaciones_generales=(
            payload.indicaciones_generales
        ),
        estado="EMITIDA",
    )

    for item in payload.items:
        prescription.items.append(
            PrescriptionItem(
                medicamento_id=item.medicamento_id,
                dosis=item.dosis,
                via_administracion=(
                    item.via_administracion
                ),
                frecuencia=item.frecuencia,
                duracion=item.duracion,
                cantidad=item.cantidad,
                cantidad_dispensada=0,
                indicaciones=item.indicaciones,
            )
        )

    database.add(prescription)

    try:
        database.commit()
        database.refresh(prescription)
    except IntegrityError as exc:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar la receta.",
        ) from exc

    stored = get_prescription_by_id(
        database,
        prescription.receta_id,
    )

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "La receta fue creada, pero no pudo recuperarse."
            ),
        )

    return prescription_to_response(stored)


def get_prescription_or_404(
    database: Session,
    prescription_id: int,
) -> Prescription:
    prescription = get_prescription_by_id(
        database,
        prescription_id,
    )

    if prescription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada.",
        )

    return prescription


def read_prescription(
    database: Session,
    prescription_id: int,
) -> PrescriptionResponse:
    return prescription_to_response(
        get_prescription_or_404(
            database,
            prescription_id,
        )
    )


def read_prescriptions(
    database: Session,
    patient_id: int | None,
    prescription_status: str | None,
    page: int,
    page_size: int,
) -> PrescriptionListResponse:
    normalized_status = (
        prescription_status.strip().upper()
        if prescription_status
        else None
    )

    prescriptions, total = list_prescriptions(
        database=database,
        patient_id=patient_id,
        prescription_status=normalized_status,
        page=page,
        page_size=page_size,
    )

    return PrescriptionListResponse(
        items=[
            prescription_to_response(prescription)
            for prescription in prescriptions
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


def dispense_prescription(
    database: Session,
    prescription_id: int,
) -> PrescriptionResponse:
    prescription = get_prescription_or_404(
        database,
        prescription_id,
    )

    if prescription.estado != "EMITIDA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Solo se pueden dispensar recetas emitidas."
            ),
        )

    for item in prescription.items:
        if not has_sufficient_stock(
            item.medicamento.stock_actual,
            item.cantidad,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Stock insuficiente para "
                    f"{item.medicamento.nombre}. "
                    f"Disponible: "
                    f"{item.medicamento.stock_actual}."
                ),
            )

    for item in prescription.items:
        medication = item.medicamento
        previous_stock = medication.stock_actual
        new_stock = calculate_new_stock(
            previous_stock,
            "SALIDA",
            item.cantidad,
        )

        medication.stock_actual = new_stock
        item.cantidad_dispensada = item.cantidad

        database.add(
            InventoryMovement(
                medicamento_id=medication.medicamento_id,
                receta_id=prescription.receta_id,
                tipo="SALIDA",
                cantidad=item.cantidad,
                stock_anterior=previous_stock,
                stock_nuevo=new_stock,
                motivo=(
                    f"Dispensación de receta "
                    f"{prescription.receta_id}"
                ),
            )
        )

    prescription.estado = "DISPENSADA"
    prescription.fecha_dispensacion = (
        datetime.now(timezone.utc).replace(tzinfo=None)
    )
    database.commit()

    updated = get_prescription_by_id(
        database,
        prescription_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar la receta dispensada."
            ),
        )

    return prescription_to_response(updated)


def cancel_prescription(
    database: Session,
    prescription_id: int,
    payload: PrescriptionCancel,
) -> PrescriptionResponse:
    prescription = get_prescription_or_404(
        database,
        prescription_id,
    )

    if prescription.estado != "EMITIDA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Solo se pueden anular recetas emitidas."
            ),
        )

    prescription.estado = "ANULADA"
    prescription.motivo_anulacion = (
        payload.motivo_anulacion
    )
    database.commit()

    updated = get_prescription_by_id(
        database,
        prescription_id,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible recuperar la receta anulada.",
        )

    return prescription_to_response(updated)
