# Módulo de laboratorio clínico

## Objetivo

Gestionar tipos de examen, órdenes médicas y resultados de laboratorio
vinculados con la consulta y el historial del paciente.

## Funcionalidades

- Catálogo de tipos de examen.
- Exámenes iniciales para pruebas.
- Precio y muestra requerida por examen.
- Órdenes vinculadas con consultas clínicas.
- Prioridad normal o urgente.
- Varios exámenes dentro de una orden.
- Estados de orden e ítems.
- Registro y actualización de resultados.
- Valores de referencia e interpretación.
- Campo opcional para archivo del resultado.
- Cierre automático cuando todos los resultados están completos.
- Búsqueda por paciente y estado.
- Protección por roles.

## Estados

```text
SOLICITADA
EN_PROCESO
COMPLETADA
CANCELADA
```

## Tablas

```text
TIPOS_EXAMEN_LABORATORIO
ORDENES_LABORATORIO
DETALLE_ORDENES_LABORATORIO
RESULTADOS_LABORATORIO
```

## Endpoints

```text
GET  /api/v1/lab-tests
POST /api/v1/lab-tests
PUT  /api/v1/lab-tests/{test_type_id}

POST  /api/v1/lab-orders
GET   /api/v1/lab-orders
GET   /api/v1/lab-orders/{order_id}
PATCH /api/v1/lab-orders/{order_id}/status
POST  /api/v1/lab-orders/{order_id}/items/{item_id}/result
```
