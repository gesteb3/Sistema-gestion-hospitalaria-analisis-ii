# Módulo de usuarios, roles y autenticación

## Objetivo

Implementar el acceso seguro al Sistema de Gestión Hospitalaria mediante
usuarios, contraseñas protegidas, roles y tokens JWT.

## Funcionalidades implementadas

- Creación automática de las tablas `USUARIOS`, `ROLES` y `USUARIO_ROLES`.
- Registro inicial de nueve roles hospitalarios.
- Creación automática del usuario administrador.
- Contraseñas protegidas con Argon2 mediante `pwdlib`.
- Inicio de sesión con OAuth2 Password y token JWT.
- Consulta del usuario autenticado.
- Registro y listado de usuarios protegido para administradores.
- Pruebas unitarias de hashing y tokens.

## Usuario inicial

- Usuario: `admin`
- Contraseña: `Admin12345`

La contraseña debe modificarse antes de utilizar el sistema en producción.

## Endpoints

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
GET  /api/v1/users
POST /api/v1/users
```

## Roles iniciales

- ADMINISTRADOR
- RECEPCIONISTA
- MEDICO
- ENFERMERO
- LABORATORIO
- FARMACIA
- CONTABILIDAD
- PACIENTE
- AUDITOR
