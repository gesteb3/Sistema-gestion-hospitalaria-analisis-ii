# Módulo de citas médicas

## Objetivo

Programar y administrar citas médicas validando automáticamente la
disponibilidad del médico, los horarios configurados y los conflictos de
agenda.

## Funcionalidades implementadas

- Programación de citas.
- Consulta individual y listado paginado.
- Filtros por paciente, médico, estado y rango de fechas.
- Consulta de espacios disponibles.
- Validación del horario semanal del médico.
- Validación de duración y alineación de cada espacio.
- Prevención de citas traslapadas para el médico.
- Prevención de citas simultáneas para el paciente.
- Reprogramación.
- Cambio controlado de estado.
- Cancelación con motivo obligatorio.
- Protección por roles.

## Estados

```text
PROGRAMADA
CONFIRMADA
COMPLETADA
CANCELADA
NO_ASISTIO
```

## Endpoints

```text
GET   /api/v1/appointments/availability
POST  /api/v1/appointments
GET   /api/v1/appointments
GET   /api/v1/appointments/{appointment_id}
PUT   /api/v1/appointments/{appointment_id}
PATCH /api/v1/appointments/{appointment_id}/status
```

## Regla principal

Una cita solo puede guardarse cuando:

1. El paciente está activo.
2. El médico está activo.
3. La fecha y hora pertenecen a un horario activo del médico.
4. El espacio coincide con la duración configurada.
5. El médico no tiene otra cita en ese espacio.
6. El paciente no tiene otra cita en ese espacio.
