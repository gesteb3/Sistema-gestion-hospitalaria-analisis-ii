# Sistema de Gestión Hospitalaria

Sistema web académico para administrar pacientes, médicos, citas, historiales,
consultas, diagnósticos, recetas, laboratorio, farmacia, pagos, usuarios,
roles y auditoría.

## Tecnologías

- Angular con TypeScript
- Python con FastAPI
- SQLAlchemy
- python-oracledb
- Oracle Database Free
- Docker Compose

## Estructura inicial

```text
backend/
  app/
    api/v1/endpoints/
    core/
    db/
    models/
    repositories/
    schemas/
    services/
    utils/
  tests/
database/
docs/
uploads/laboratorio/
docker-compose.yml
```

## Iniciar con Docker desde CMD

1. Crear el archivo local de variables:

```cmd
copy .env.example .env
```

2. Construir y levantar los contenedores:

```cmd
docker compose up --build
```

La primera descarga de Oracle puede tardar porque la imagen es grande.

3. Abrir:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Estado general: http://localhost:8000/api/v1/health
- Estado de Oracle: http://localhost:8000/api/v1/health/database

4. Detener:

```cmd
docker compose down
```

5. Detener y borrar también los datos locales de Oracle:

```cmd
docker compose down -v
```

## Ejecutar pruebas

```cmd
docker compose exec backend pytest
```

## Autor

Gustavo Adolfo Esteban Batres
