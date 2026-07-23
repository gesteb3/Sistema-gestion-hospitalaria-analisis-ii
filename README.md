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

- Usuarios, roles y autenticación JWT.
- Pacientes y responsables legales.
- Especialidades, médicos y horarios.
- Citas médicas.
- Historial clínico y consultas.
- Signos vitales, diagnósticos y tratamientos.
- Medicamentos e inventario.
- Recetas y dispensación.

## Iniciar el sistema

```powershell
Copy-Item .env.example .env -Force
docker compose up -d --build
```

## Direcciones

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Oracle: http://localhost:8000/api/v1/health/database

## Usuario inicial

- Usuario: `admin`
- Contraseña: `Admin12345`

## Pruebas

```powershell
docker compose exec backend pytest
```

## Autor

Gustavo Adolfo Esteban Batres
