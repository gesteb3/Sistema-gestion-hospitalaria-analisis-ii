# Frontend Angular v2 — Sistema de Gestión Hospitalaria

Versión funcional ampliada conectada con los endpoints reales de FastAPI.

## Módulos con acciones reales

- Dashboard.
- Pacientes: crear, editar, desactivar y reactivar; responsable legal para menores.
- Médicos: crear, editar, desactivar, reactivar y administrar horarios.
- Citas: programar, reprogramar, confirmar, cancelar y marcar no asistencia.
- Consultas clínicas: signos vitales, diagnóstico y tratamiento.
- Especialidades: crear, editar, desactivar y reactivar.
- Usuarios: listar y crear cuentas con roles.
- Medicamentos: crear, editar y registrar entradas o ajustes de inventario.
- Recetas: emitir, dispensar y anular.
- Laboratorio: tipos de examen, órdenes, procesamiento y resultados.
- Facturación: facturas, pagos parciales/completos y anulación.
- Auditoría y reportes.
- Habitaciones se mantiene pendiente porque no existe endpoint en el backend.

## Ejecución

```powershell
cd frontend
npm install
npm start
```

Frontend: http://localhost:4200  
Backend: http://localhost:8000  
Usuario: `admin`  
Contraseña: `Admin12345`


## Corrección v2.1

Se corrigieron cierres duplicados de bloques Angular `@if` y `@for` en nueve componentes que producían el error `NG5002: Unexpected closing block`.
