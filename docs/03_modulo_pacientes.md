# Módulo de pacientes y responsables legales

## Objetivo

Administrar el expediente básico de los pacientes del hospital y registrar
un responsable legal cuando el paciente sea menor de edad.

## Funcionalidades implementadas

- Registro de pacientes.
- Generación automática del número de expediente.
- Validación de identificación duplicada.
- Validación de fecha de nacimiento.
- Registro obligatorio de responsable legal para menores de edad.
- Consulta individual.
- Listado paginado.
- Búsqueda por expediente, nombres, apellidos o identificación.
- Actualización de datos.
- Desactivación lógica.
- Reactivación de pacientes.
- Acceso protegido por roles.

## Formato del expediente

```text
EXP-2026-000001
```

El año corresponde al año de creación y el número final utiliza el
identificador interno del paciente.

## Roles autorizados

### Lectura

- ADMINISTRADOR
- RECEPCIONISTA
- MEDICO
- ENFERMERO
- LABORATORIO
- CONTABILIDAD
- AUDITOR

### Escritura

- ADMINISTRADOR
- RECEPCIONISTA

## Endpoints

```text
POST   /api/v1/patients
GET    /api/v1/patients
GET    /api/v1/patients/{patient_id}
PUT    /api/v1/patients/{patient_id}
DELETE /api/v1/patients/{patient_id}
PATCH  /api/v1/patients/{patient_id}/reactivate
```

## Regla para menores de edad

Cuando la edad calculada sea menor de 18 años, el sistema exige los datos de
un responsable legal antes de completar el registro.
