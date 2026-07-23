# Módulo de auditoría y reportes

## Objetivo

Registrar automáticamente las operaciones realizadas sobre la API y ofrecer
indicadores resumidos para supervisar el funcionamiento clínico,
administrativo y financiero del hospital.

## Auditoría

La bitácora guarda:

- Usuario identificado por JWT.
- Acción ejecutada.
- Módulo.
- Método HTTP.
- Ruta solicitada.
- Código de respuesta.
- Resultado exitoso o fallido.
- Dirección IP.
- Duración en milisegundos.
- Fecha del evento.

No se almacenan contraseñas ni cuerpos completos de las solicitudes.

## Reportes

```text
GET /api/v1/reports/dashboard
GET /api/v1/reports/clinical
GET /api/v1/reports/financial
GET /api/v1/reports/system
```

## Consulta de bitácora

```text
GET /api/v1/audit-logs
```

Filtros disponibles:

```text
username
module
method
successful
date_from
date_to
page
page_size
```

## Tabla

```text
BITACORA_AUDITORIA
```

## Dashboard

El resumen presenta:

- Pacientes y médicos activos.
- Citas programadas.
- Consultas realizadas.
- Órdenes de laboratorio pendientes.
- Recetas emitidas.
- Medicamentos con stock bajo.
- Facturas pendientes.
- Total facturado.
- Total pagado.
- Saldo pendiente.
