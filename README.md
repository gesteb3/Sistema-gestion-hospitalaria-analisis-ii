# Sistema de Gestión Hospitalaria

Aplicación web académica para administrar procesos clínicos y administrativos
de un hospital.

## Tecnologías

- Angular con TypeScript
- Python con FastAPI
- SQLAlchemy
- python-oracledb
- Oracle Database Free
- Docker Compose
- JWT y OAuth2 Password

## Módulos implementados

- Estado general de la API y conexión con Oracle.
- Usuarios y roles.
- Autenticación JWT.
- Pacientes.
- Responsables legales.

## Iniciar el sistema

```cmd
copy /Y .env.example .env
docker compose up -d --build
```

## Direcciones

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Estado: http://localhost:8000/api/v1/health
- Oracle: http://localhost:8000/api/v1/health/database

## Usuario inicial

- Usuario: `admin`
- Contraseña: `Admin12345`

## Pruebas

```cmd
docker compose exec backend pytest
```

## Autor

Gustavo Adolfo Esteban Batres
