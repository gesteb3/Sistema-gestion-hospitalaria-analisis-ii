# Módulo de farmacia y recetas

## Objetivo

Administrar los medicamentos disponibles, registrar recetas vinculadas con
consultas clínicas y controlar automáticamente las existencias al dispensar.

## Funcionalidades

- Catálogo de medicamentos.
- Medicamentos iniciales para pruebas.
- Control de stock actual y mínimo.
- Identificación de productos con stock bajo.
- Entradas y ajustes de inventario.
- Receta vinculada con una consulta clínica.
- Una receta por consulta.
- Detalle de dosis, vía, frecuencia y duración.
- Validación de medicamentos activos.
- Dispensación con control de existencias.
- Descuento automático de inventario.
- Registro de movimientos de salida.
- Anulación de recetas no dispensadas.
- Protección por roles.

## Estados de receta

```text
EMITIDA
DISPENSADA
ANULADA
```

## Tablas

```text
MEDICAMENTOS
RECETAS
DETALLE_RECETAS
MOVIMIENTOS_INVENTARIO
```

## Endpoints

```text
POST /api/v1/medications
GET  /api/v1/medications
GET  /api/v1/medications/{medication_id}
PUT  /api/v1/medications/{medication_id}
POST /api/v1/medications/{medication_id}/stock

POST  /api/v1/prescriptions
GET   /api/v1/prescriptions
GET   /api/v1/prescriptions/{prescription_id}
PATCH /api/v1/prescriptions/{prescription_id}/dispense
PATCH /api/v1/prescriptions/{prescription_id}/cancel
```
