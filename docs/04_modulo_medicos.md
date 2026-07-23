# Módulo de médicos, especialidades y horarios

## Objetivo

Administrar el personal médico, sus especialidades profesionales y los
horarios disponibles para posteriormente programar citas.

## Funcionalidades implementadas

- Catálogo de especialidades.
- Registro de médicos.
- Número de colegiado único.
- Correo profesional único.
- Asignación de una o varias especialidades.
- Listado paginado y búsqueda de médicos.
- Filtrado por especialidad.
- Actualización y desactivación lógica.
- Registro de horarios semanales.
- Validación de formato de hora.
- Prevención de horarios traslapados.
- Duración configurable de cada espacio de cita.
- Permisos por rol.

## Especialidades iniciales

- Medicina General
- Pediatría
- Medicina Interna
- Ginecología
- Cardiología

## Días de la semana

```text
1 = Lunes
2 = Martes
3 = Miércoles
4 = Jueves
5 = Viernes
6 = Sábado
7 = Domingo
```

## Endpoints de especialidades

```text
GET    /api/v1/specialties
GET    /api/v1/specialties/{specialty_id}
POST   /api/v1/specialties
PUT    /api/v1/specialties/{specialty_id}
DELETE /api/v1/specialties/{specialty_id}
PATCH  /api/v1/specialties/{specialty_id}/reactivate
```

## Endpoints de médicos

```text
GET    /api/v1/doctors
GET    /api/v1/doctors/{doctor_id}
POST   /api/v1/doctors
PUT    /api/v1/doctors/{doctor_id}
DELETE /api/v1/doctors/{doctor_id}
PATCH  /api/v1/doctors/{doctor_id}/reactivate
```

## Endpoints de horarios

```text
GET    /api/v1/doctors/{doctor_id}/schedules
POST   /api/v1/doctors/{doctor_id}/schedules
PUT    /api/v1/doctors/{doctor_id}/schedules/{schedule_id}
DELETE /api/v1/doctors/{doctor_id}/schedules/{schedule_id}
```
