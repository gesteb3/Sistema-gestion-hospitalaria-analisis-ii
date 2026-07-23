# Módulo de facturación y pagos

## Objetivo

Registrar los servicios cobrados al paciente, generar facturas y controlar
pagos completos o parciales.

## Funcionalidades

- Factura vinculada con paciente.
- Relación opcional con consulta clínica.
- Número automático de factura.
- Detalle de servicios, medicamentos o exámenes.
- Cálculo de subtotal, descuento y total.
- Pagos parciales.
- Saldo pendiente.
- Estados automáticos.
- Distintos métodos de pago.
- Anulación únicamente cuando no existen pagos.
- Resumen financiero.
- Protección por roles.

## Estados

```text
PENDIENTE
PARCIAL
PAGADA
ANULADA
```

## Métodos de pago

```text
EFECTIVO
TARJETA
TRANSFERENCIA
CHEQUE
```

## Tablas

```text
FACTURAS
DETALLE_FACTURAS
PAGOS
```

## Endpoints

```text
GET   /api/v1/billing/summary
POST  /api/v1/billing/invoices
GET   /api/v1/billing/invoices
GET   /api/v1/billing/invoices/{invoice_id}
PUT   /api/v1/billing/invoices/{invoice_id}
POST  /api/v1/billing/invoices/{invoice_id}/payments
PATCH /api/v1/billing/invoices/{invoice_id}/cancel
```
