# Módulo clínico

## Objetivo

Concentrar la información médica del paciente en un historial clínico y
registrar cada atención relacionada con una cita médica.

## Funcionalidades

- Historial clínico único por paciente.
- Antecedentes, alergias, enfermedades crónicas y cirugías previas.
- Consulta clínica vinculada con una cita.
- Validación de paciente, médico y cita.
- Una sola consulta por cita.
- Cierre automático de la cita al registrar la consulta.
- Signos vitales.
- Cálculo automático del índice de masa corporal.
- Diagnósticos presuntivos, definitivos y diferenciales.
- Un diagnóstico principal por consulta.
- Tratamientos e indicaciones.
- Consulta cronológica del historial.
- Acceso protegido por roles.

## Tablas

```text
HISTORIALES_CLINICOS
CONSULTAS
SIGNOS_VITALES
DIAGNOSTICOS
TRATAMIENTOS
```

## Endpoints

```text
GET  /api/v1/clinical-histories/patient/{patient_id}
PUT  /api/v1/clinical-histories/patient/{patient_id}

POST /api/v1/consultations
GET  /api/v1/consultations
GET  /api/v1/consultations/{consultation_id}
PUT  /api/v1/consultations/{consultation_id}

PUT  /api/v1/consultations/{consultation_id}/vital-signs
POST /api/v1/consultations/{consultation_id}/diagnoses
POST /api/v1/consultations/{consultation_id}/treatments
```

## Regla principal

Para registrar una consulta debe existir una cita que corresponda al médico.
La cita no puede estar cancelada ni marcada como no asistida. Al finalizar el
registro clínico, la cita cambia automáticamente a estado COMPLETADA.
