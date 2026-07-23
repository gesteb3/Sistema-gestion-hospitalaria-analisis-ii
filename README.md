# Sistema de Gestión Hospitalaria

Aplicación web académica para administrar procesos clínicos y administrativos
de un hospital.

## Módulos implementados

- Usuarios, roles y autenticación JWT.
- Pacientes y responsables legales.
- Especialidades, médicos y horarios.
- Citas médicas.
- Historial clínico y consultas.
- Signos vitales, diagnósticos y tratamientos.
- Medicamentos, recetas e inventario.
- Tipos de examen, órdenes y resultados de laboratorio.

## Iniciar

```powershell
Copy-Item .env.example .env -Force
docker compose up -d --build
```

## Swagger

```text
http://localhost:8000/docs
```

## Usuario

- Usuario: `admin`
- Contraseña: `Admin12345`

## Pruebas

```powershell
docker compose exec backend pytest
```

## Autor

Gustavo Adolfo Esteban Batres
