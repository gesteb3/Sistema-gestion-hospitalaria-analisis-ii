# Sistema de Gestión Hospitalaria

Aplicación web académica para administrar procesos clínicos y administrativos
de un hospital.

## Backend implementado

- Usuarios, roles y autenticación JWT.
- Pacientes y responsables legales.
- Especialidades, médicos y horarios.
- Citas médicas y disponibilidad.
- Historial clínico y consultas.
- Signos vitales, diagnósticos y tratamientos.
- Medicamentos, recetas e inventario.
- Órdenes y resultados de laboratorio.
- Facturación y pagos.
- Auditoría automática.
- Reportes clínicos, financieros y operativos.
- Resumen para dashboard.

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
