import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';
import {
  FormArray,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';

import { ApiService } from '../../core/api.service';
import { apiError } from '../../core/api-error';
import {
  BillingSummary,
  Consultation,
  Invoice,
  InvoiceCreate,
  Patient,
} from '../../core/models';

@Component({
  selector: 'app-billing',
  imports: [
    CommonModule,
    ReactiveFormsModule,
  ],
  template: `
    <section class="page-header">
      <div>
        <span class="eyebrow">
          Administración financiera
        </span>

        <h1>Facturación y pagos</h1>

        <p>
          Generá facturas, registrá abonos y controlá
          los saldos pendientes.
        </p>
      </div>

      <button
        type="button"
        class="button primary"
        (click)="openInvoice()"
      >
        + Nueva factura
      </button>
    </section>

    @if (message()) {
      <div class="success">
        {{ message() }}
      </div>
    }

    @if (
      error()
      && !invoiceOpen()
      && !paymentOpen()
    ) {
      <div class="alert">
        {{ error() }}
      </div>
    }

    @if (summary(); as data) {
      <section class="summary">
        <article>
          <small>Total facturado</small>

          <strong>
            {{
              data.total_facturado
                | currency:'GTQ':'symbol-narrow'
            }}
          </strong>
        </article>

        <article>
          <small>Total pagado</small>

          <strong>
            {{
              data.total_pagado
                | currency:'GTQ':'symbol-narrow'
            }}
          </strong>
        </article>

        <article>
          <small>Saldo pendiente</small>

          <strong>
            {{
              data.saldo_pendiente
                | currency:'GTQ':'symbol-narrow'
            }}
          </strong>
        </article>

        <article>
          <small>Facturas pendientes</small>

          <strong>
            {{
              data.facturas_pendientes
              + data.facturas_parciales
            }}
          </strong>
        </article>
      </section>
    }

    <section class="panel list-panel">
      @if (loading()) {
        <div class="loading">
          Cargando facturas...
        </div>
      } @else if (invoices().length > 0) {
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Factura</th>
                <th>Paciente</th>
                <th>Total</th>
                <th>Pagado</th>
                <th>Saldo</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              @for (
                invoice of invoices();
                track invoice.factura_id
              ) {
                <tr>
                  <td>
                    <strong>
                      {{ invoice.numero_factura }}
                    </strong>

                    <small>
                      {{
                        invoice.fecha_emision
                          | date:'dd/MM/yyyy'
                      }}
                    </small>
                  </td>

                  <td>
                    <strong>
                      {{ invoice.paciente_nombre }}
                    </strong>

                    <small>
                      NIT: {{ invoice.nit }}
                    </small>
                  </td>

                  <td>
                    {{
                      invoice.total
                        | currency:'GTQ':'symbol-narrow'
                    }}
                  </td>

                  <td>
                    {{
                      invoice.total_pagado
                        | currency:'GTQ':'symbol-narrow'
                    }}
                  </td>

                  <td>
                    {{
                      invoice.saldo_pendiente
                        | currency:'GTQ':'symbol-narrow'
                    }}
                  </td>

                  <td>
                    <span
                      class="badge"
                      [attr.data-status]="invoice.estado"
                    >
                      {{ invoice.estado }}
                    </span>
                  </td>

                  <td>
                    <div class="row-actions">
                      @if (
                        invoice.estado !== 'PAGADA'
                        && invoice.estado !== 'ANULADA'
                      ) {
                        <button
                          type="button"
                          (click)="payment(invoice)"
                        >
                          Pago
                        </button>
                      }

                      @if (
                        Number(invoice.total_pagado) === 0
                        && invoice.estado !== 'ANULADA'
                      ) {
                        <button
                          type="button"
                          class="danger-btn"
                          (click)="cancel(invoice)"
                        >
                          Anular
                        </button>
                      }
                    </div>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      } @else {
        <div class="empty">
          <strong>No hay facturas registradas</strong>

          <p>
            Presioná “Nueva factura” para generar
            el primer cobro hospitalario.
          </p>
        </div>
      }
    </section>

    @if (invoiceOpen()) {
      <div
        class="drawer-backdrop"
        (click)="closeInvoice()"
      >
        <aside
          class="drawer wide"
          (click)="$event.stopPropagation()"
        >
          <div class="drawer-title">
            <div>
              <span class="eyebrow">
                Cobro hospitalario
              </span>

              <h2>Nueva factura</h2>
            </div>

            <button
              type="button"
              aria-label="Cerrar formulario"
              (click)="closeInvoice()"
            >
              ×
            </button>
          </div>

          @if (error()) {
            <div class="alert drawer-alert">
              {{ error() }}
            </div>
          }

          <form
            [formGroup]="invoiceForm"
            (ngSubmit)="saveInvoice()"
          >
            <div class="form-grid">
              <label>
                <span>Paciente *</span>

                <select
                  formControlName="paciente_id"
                  (change)="patientChanged()"
                >
                  <option [ngValue]="null">
                    Seleccionar paciente
                  </option>

                  @for (
                    patient of patients();
                    track patient.paciente_id
                  ) {
                    <option
                      [ngValue]="patient.paciente_id"
                    >
                      {{ patient.numero_expediente }}
                      · {{ patient.nombres }}
                      {{ patient.apellidos }}
                    </option>
                  }
                </select>

                @if (
                  invoiceForm.controls.paciente_id.touched
                  && invoiceForm.controls.paciente_id.invalid
                ) {
                  <small class="field-error">
                    Seleccioná un paciente.
                  </small>
                }
              </label>

              <label>
                <span>Consulta relacionada</span>

                <select formControlName="consulta_id">
                  <option [ngValue]="null">
                    Ninguna
                  </option>

                  @for (
                    consultation of consultations();
                    track consultation.consulta_id
                  ) {
                    <option
                      [ngValue]="consultation.consulta_id"
                    >
                      Consulta #{{ consultation.consulta_id }}
                      · {{ consultation.paciente_nombre }}
                    </option>
                  }
                </select>
              </label>

              <label>
                <span>NIT *</span>

                <input
                  formControlName="nit"
                  placeholder="Ejemplo: CF o 1234567-8"
                >

                @if (
                  invoiceForm.controls.nit.touched
                  && invoiceForm.controls.nit.invalid
                ) {
                  <small class="field-error">
                    El NIT es obligatorio.
                  </small>
                }
              </label>

              <label>
                <span>Nombre de facturación *</span>

                <input
                  formControlName="nombre_facturacion"
                  placeholder="Ejemplo: Carlos Pérez"
                >

                @if (
                  invoiceForm.controls
                    .nombre_facturacion.touched
                  && invoiceForm.controls
                    .nombre_facturacion.invalid
                ) {
                  <small class="field-error">
                    Ingresá el nombre de facturación.
                  </small>
                }
              </label>

              <label class="full">
                <span>Dirección de facturación</span>

                <input
                  formControlName="direccion_facturacion"
                  placeholder="Ejemplo: Quetzaltenango"
                >
              </label>

              <label>
                <span>Descuento</span>

                <div class="money-input">
                  <span>Q</span>

                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    formControlName="descuento"
                    placeholder="0.00"
                  >
                </div>
              </label>

              <label>
                <span>Observaciones</span>

                <input
                  formControlName="observaciones"
                  placeholder="Ejemplo: Servicios médicos"
                >
              </label>
            </div>

            <div class="line-heading">
              <div>
                <strong>Detalle de cobro</strong>

                <small>
                  Agregá cada servicio incluido
                  en la factura.
                </small>
              </div>

              <button
                type="button"
                (click)="addLine()"
              >
                + Agregar servicio
              </button>
            </div>

            <div
              formArrayName="items"
              class="invoice-lines"
            >
              @for (
                group of lines.controls;
                track $index;
                let index = $index
              ) {
                <div
                  class="invoice-line"
                  [formGroupName]="index"
                >
                  <div class="line-title">
                    Servicio {{ index + 1 }}
                  </div>

                  <label>
                    <span>Tipo de servicio *</span>

                    <select formControlName="tipo_servicio">
                      <option value="CONSULTA">
                        Consulta médica
                      </option>

                      <option value="LABORATORIO">
                        Examen de laboratorio
                      </option>

                      <option value="MEDICAMENTO">
                        Medicamento
                      </option>

                      <option value="HOSPITALIZACION">
                        Hospitalización
                      </option>

                      <option value="OTRO">
                        Otro servicio
                      </option>
                    </select>
                  </label>

                  <label class="description-field">
                    <span>Descripción *</span>

                    <input
                      formControlName="descripcion"
                      placeholder="Ejemplo: Consulta de medicina general"
                    >

                    @if (
                      group.controls.descripcion.touched
                      && group.controls.descripcion.invalid
                    ) {
                      <small class="field-error">
                        Ingresá la descripción del servicio.
                      </small>
                    }
                  </label>

                  <label>
                    <span>Cantidad *</span>

                    <input
                      type="number"
                      min="1"
                      step="1"
                      formControlName="cantidad"
                      placeholder="Ejemplo: 1"
                    >

                    @if (
                      group.controls.cantidad.touched
                      && group.controls.cantidad.invalid
                    ) {
                      <small class="field-error">
                        La cantidad debe ser mayor o igual a 1.
                      </small>
                    }
                  </label>

                  <label>
                    <span>Precio unitario *</span>

                    <div class="money-input">
                      <span>Q</span>

                      <input
                        type="number"
                        min="0.01"
                        step="0.01"
                        formControlName="precio_unitario"
                        placeholder="150.00"
                      >
                    </div>

                    @if (
                      group.controls.precio_unitario.touched
                      && group.controls.precio_unitario.invalid
                    ) {
                      <small class="field-error">
                        El precio debe ser mayor a cero.
                      </small>
                    }
                  </label>

                  <div class="subtotal">
                    <span>Subtotal</span>

                    <strong>
                      {{
                        calculateLineSubtotal(index)
                          | currency:'GTQ':'symbol-narrow'
                      }}
                    </strong>
                  </div>

                  <button
                    type="button"
                    class="remove-line"
                    title="Quitar servicio"
                    [disabled]="lines.length === 1"
                    (click)="removeLine(index)"
                  >
                    ×
                  </button>
                </div>
              }
            </div>

            <section class="invoice-totals">
              <div>
                <span>Subtotal</span>

                <strong>
                  {{
                    invoiceSubtotal()
                      | currency:'GTQ':'symbol-narrow'
                  }}
                </strong>
              </div>

              <div>
                <span>Descuento</span>

                <strong>
                  {{
                    invoiceDiscount()
                      | currency:'GTQ':'symbol-narrow'
                  }}
                </strong>
              </div>

              <div class="grand-total">
                <span>Total de la factura</span>

                <strong>
                  {{
                    invoiceTotal()
                      | currency:'GTQ':'symbol-narrow'
                  }}
                </strong>
              </div>
            </section>

            @if (
              invoiceForm.invalid
              && invoiceForm.touched
            ) {
              <div class="form-warning">
                Completá paciente, NIT, nombre de
                facturación y todos los detalles de cobro.
              </div>
            }

            <div class="actions sticky-actions">
              <button
                type="button"
                class="button secondary"
                (click)="closeInvoice()"
              >
                Cancelar
              </button>

              <button
                type="submit"
                class="button primary"
                [disabled]="saving()"
              >
                {{
                  saving()
                    ? 'Generando...'
                    : 'Generar factura'
                }}
              </button>
            </div>
          </form>
        </aside>
      </div>
    }

    @if (paymentOpen() && selected()) {
      <div
        class="drawer-backdrop"
        (click)="closePayment()"
      >
        <aside
          class="drawer small"
          (click)="$event.stopPropagation()"
        >
          <div class="drawer-title">
            <div>
              <span class="eyebrow">
                Registrar pago
              </span>

              <h2>
                {{ selected()!.numero_factura }}
              </h2>

              <p>
                Saldo pendiente:
                {{
                  selected()!.saldo_pendiente
                    | currency:'GTQ':'symbol-narrow'
                }}
              </p>
            </div>

            <button
              type="button"
              aria-label="Cerrar pago"
              (click)="closePayment()"
            >
              ×
            </button>
          </div>

          @if (error()) {
            <div class="alert drawer-alert">
              {{ error() }}
            </div>
          }

          <form
            class="form-grid"
            [formGroup]="paymentForm"
            (ngSubmit)="savePayment()"
          >
            <label class="full">
              <span>Monto del pago *</span>

              <div class="money-input">
                <span>Q</span>

                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  formControlName="monto"
                  placeholder="Ejemplo: 100.00"
                >
              </div>

              @if (
                paymentForm.controls.monto.touched
                && paymentForm.controls.monto.invalid
              ) {
                <small class="field-error">
                  Ingresá un monto mayor a cero.
                </small>
              }
            </label>

            <label class="full">
              <span>Método de pago *</span>

              <select formControlName="metodo_pago">
                <option value="EFECTIVO">
                  Efectivo
                </option>

                <option value="TARJETA">
                  Tarjeta
                </option>

                <option value="TRANSFERENCIA">
                  Transferencia
                </option>

                <option value="CHEQUE">
                  Cheque
                </option>
              </select>
            </label>

            <label class="full">
              <span>Referencia</span>

              <input
                formControlName="referencia"
                placeholder="Número de transferencia o cheque"
              >
            </label>

            <label class="full">
              <span>Observaciones</span>

              <textarea
                rows="3"
                formControlName="observaciones"
                placeholder="Ejemplo: Primer abono de la factura"
              ></textarea>
            </label>

            <div class="actions full sticky-actions">
              <button
                type="button"
                class="button secondary"
                (click)="closePayment()"
              >
                Cancelar
              </button>

              <button
                type="submit"
                class="button primary"
                [disabled]="saving()"
              >
                {{
                  saving()
                    ? 'Aplicando...'
                    : 'Aplicar pago'
                }}
              </button>
            </div>
          </form>
        </aside>
      </div>
    }
  `,
  styles: [`
    .summary {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-top: 20px;
    }

    .summary article {
      padding: 18px;
      border: 1px solid var(--border);
      border-radius: 16px;
      background: white;
    }

    .summary small,
    .summary strong {
      display: block;
    }

    .summary small {
      color: var(--muted);
      font-size: 0.67rem;
    }

    .summary strong {
      margin-top: 8px;
      font-size: 1.2rem;
    }

    .row-actions {
      display: flex;
      gap: 5px;
    }

    .row-actions button {
      border: 0;
      border-radius: 8px;
      padding: 6px 8px;
      color: #175cd3;
      background: #eaf2ff;
      font-size: 0.6rem;
      font-weight: 800;
      cursor: pointer;
    }

    .row-actions .danger-btn {
      color: #b42318;
      background: #feeceb;
    }

    .wide {
      max-width: 980px;
    }

    .small {
      max-width: 460px;
    }

    .drawer-title p {
      margin: 5px 0 0;
      color: var(--muted);
      font-size: 0.7rem;
    }

    .drawer-alert {
      margin: 0 0 18px;
    }

    .line-heading {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin: 22px 0 12px;
    }

    .line-heading strong,
    .line-heading small {
      display: block;
    }

    .line-heading strong {
      font-size: 0.86rem;
    }

    .line-heading small {
      margin-top: 4px;
      color: var(--muted);
      font-size: 0.65rem;
    }

    .line-heading button {
      border: 0;
      color: var(--primary);
      background: transparent;
      font-size: 0.68rem;
      font-weight: 800;
      cursor: pointer;
    }

    .invoice-lines {
      display: grid;
      gap: 12px;
    }

    .invoice-line {
      display: grid;
      grid-template-columns:
        minmax(145px, 0.8fr)
        minmax(220px, 1.6fr)
        minmax(90px, 0.55fr)
        minmax(145px, 0.8fr)
        minmax(120px, 0.65fr)
        34px;
      align-items: start;
      gap: 10px;
      padding: 15px;
      border: 1px solid var(--border);
      border-radius: 13px;
      background: #fafcff;
    }

    .line-title {
      grid-column: 1 / -1;
      color: var(--primary);
      font-size: 0.65rem;
      font-weight: 900;
      text-transform: uppercase;
    }

    .invoice-line label {
      display: grid;
      gap: 6px;
    }

    .invoice-line label > span {
      font-size: 0.64rem;
      font-weight: 800;
    }

    .invoice-line select,
    .invoice-line input {
      width: 100%;
      min-height: 40px;
      padding: 7px 9px;
      border: 1px solid var(--border);
      border-radius: 8px;
      outline: none;
      background: white;
    }

    .invoice-line select:focus,
    .invoice-line input:focus {
      border-color: #84adff;
      box-shadow:
        0 0 0 3px rgb(21 94 239 / 9%);
    }

    .invoice-line input.ng-invalid.ng-touched,
    .invoice-line select.ng-invalid.ng-touched {
      border-color: #f97066;
      background: #fffafa;
    }

    .money-input {
      display: flex;
      align-items: center;
      overflow: hidden;
      border: 1px solid var(--border);
      border-radius: 9px;
      background: white;
    }

    .money-input > span {
      display: grid;
      min-height: 40px;
      padding: 0 10px;
      place-items: center;
      border-right: 1px solid var(--border);
      color: var(--muted);
      background: #f8fafc;
      font-size: 0.72rem;
      font-weight: 800;
    }

    .money-input input {
      border: 0;
      border-radius: 0;
      box-shadow: none;
    }

    .subtotal {
      display: grid;
      min-height: 65px;
      align-content: center;
      gap: 6px;
    }

    .subtotal span {
      color: var(--muted);
      font-size: 0.64rem;
    }

    .subtotal strong {
      color: var(--text);
      font-size: 0.83rem;
    }

    .remove-line {
      width: 32px;
      height: 40px;
      margin-top: 21px;
      border: 0;
      border-radius: 8px;
      color: #b42318;
      background: #feeceb;
      font-size: 1rem;
      font-weight: 900;
      cursor: pointer;
    }

    .remove-line:disabled {
      color: #98a2b3;
      background: #f2f4f7;
      cursor: not-allowed;
    }

    .invoice-totals {
      display: grid;
      width: min(100%, 390px);
      gap: 10px;
      margin: 20px 0 0 auto;
      padding: 16px;
      border: 1px solid var(--border);
      border-radius: 13px;
      background: #f8fafc;
    }

    .invoice-totals > div {
      display: flex;
      justify-content: space-between;
      gap: 15px;
      color: var(--muted);
      font-size: 0.72rem;
    }

    .invoice-totals strong {
      color: var(--text);
    }

    .invoice-totals .grand-total {
      padding-top: 11px;
      border-top: 1px solid var(--border);
      color: var(--text);
      font-weight: 800;
    }

    .grand-total strong {
      color: var(--primary);
      font-size: 1rem;
    }

    .field-error {
      color: #b42318;
      font-size: 0.6rem;
      line-height: 1.45;
    }

    .form-warning {
      margin-top: 15px;
      padding: 11px 13px;
      border: 1px solid #fedf89;
      border-radius: 10px;
      color: #93370d;
      background: #fffaeb;
      font-size: 0.7rem;
      line-height: 1.5;
    }

    .sticky-actions {
      position: sticky;
      z-index: 5;
      bottom: -24px;
      margin: 20px -24px -24px;
      padding: 15px 24px;
      border-top: 1px solid var(--border);
      background: white;
    }

    table small,
    table strong {
      display: block;
    }

    table small {
      margin-top: 4px;
      color: #98a2b3;
      font-size: 0.6rem;
    }

    @media (max-width: 1050px) {
      .invoice-line {
        grid-template-columns:
          repeat(2, minmax(0, 1fr));
      }

      .line-title,
      .description-field {
        grid-column: 1 / -1;
      }

      .remove-line {
        margin-top: 0;
      }
    }

    @media (max-width: 900px) {
      .summary {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 600px) {
      .summary {
        grid-template-columns: 1fr;
      }

      .invoice-line {
        grid-template-columns: 1fr;
      }

      .line-title,
      .description-field {
        grid-column: auto;
      }

      .line-heading {
        flex-direction: column;
      }

      .sticky-actions {
        bottom: -20px;
        margin: 20px -16px -20px;
        padding: 14px 16px;
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BillingComponent {
  private readonly api = inject(ApiService);

  readonly summary =
    signal<BillingSummary | null>(null);

  readonly invoices = signal<Invoice[]>([]);
  readonly patients = signal<Patient[]>([]);
  readonly consultations =
    signal<Consultation[]>([]);

  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly invoiceOpen = signal(false);
  readonly paymentOpen = signal(false);
  readonly selected =
    signal<Invoice | null>(null);

  readonly error = signal('');
  readonly message = signal('');

  readonly invoiceForm = new FormGroup({
    paciente_id: new FormControl<number | null>(
      null,
      Validators.required,
    ),

    consulta_id: new FormControl<number | null>(
      null,
    ),

    nit: new FormControl('CF', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(20),
      ],
    }),

    nombre_facturacion: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(200),
      ],
    }),

    direccion_facturacion: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.maxLength(300),
      ],
    }),

    descuento: new FormControl(0, {
      nonNullable: true,
      validators: [
        Validators.min(0),
      ],
    }),

    observaciones: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.maxLength(1000),
      ],
    }),

    items: new FormArray([
      this.lineGroup(),
    ]),
  });

  readonly paymentForm = new FormGroup({
    monto: new FormControl(0, {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.min(0.01),
      ],
    }),

    metodo_pago: new FormControl(
      'EFECTIVO',
      {
        nonNullable: true,
        validators: [Validators.required],
      },
    ),

    referencia: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.maxLength(150),
      ],
    }),

    observaciones: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.maxLength(500),
      ],
    }),
  });

  get lines() {
    return this.invoiceForm.controls.items;
  }

  constructor() {
    this.reload();
    this.loadPatients();
    this.loadConsultations();
  }

  lineGroup() {
    return new FormGroup({
      tipo_servicio: new FormControl(
        'CONSULTA',
        {
          nonNullable: true,
          validators: [
            Validators.required,
          ],
        },
      ),

      descripcion: new FormControl('', {
        nonNullable: true,
        validators: [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(250),
        ],
      }),

      cantidad: new FormControl(1, {
        nonNullable: true,
        validators: [
          Validators.required,
          Validators.min(1),
          Validators.max(1000),
        ],
      }),

      precio_unitario: new FormControl(0, {
        nonNullable: true,
        validators: [
          Validators.required,
          Validators.min(0.01),
        ],
      }),
    });
  }

  loadPatients(): void {
    this.api.patients().subscribe({
      next: (response) => {
        this.patients.set(response.items);
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });
  }

  loadConsultations(): void {
    this.api.consultations().subscribe({
      next: (response) => {
        this.consultations.set(response.items);
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });
  }

  reload(): void {
    this.loading.set(true);

    this.api.billingSummary().subscribe({
      next: (response) => {
        this.summary.set(response);
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });

    this.api.invoices().subscribe({
      next: (response) => {
        this.invoices.set(response.items);
        this.loading.set(false);
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
        this.loading.set(false);
      },
    });
  }

  openInvoice(): void {
    this.error.set('');
    this.message.set('');

    this.invoiceForm.reset({
      paciente_id: null,
      consulta_id: null,
      nit: 'CF',
      nombre_facturacion: '',
      direccion_facturacion: '',
      descuento: 0,
      observaciones: '',
    });

    while (this.lines.length > 0) {
      this.lines.removeAt(0);
    }

    this.addLine();
    this.invoiceOpen.set(true);
  }

  addLine(): void {
    this.lines.push(this.lineGroup());
  }

  removeLine(index: number): void {
    if (this.lines.length > 1) {
      this.lines.removeAt(index);
    }
  }

  patientChanged(): void {
    const patientId =
      this.invoiceForm.controls.paciente_id.value;

    const patient = this.patients().find(
      (item) =>
        item.paciente_id === patientId,
    );

    if (!patient) {
      return;
    }

    this.invoiceForm.patchValue({
      nombre_facturacion:
        `${patient.nombres} ${patient.apellidos}`,
      direccion_facturacion:
        patient.direccion ?? '',
      nit:
        patient.identificacion ?? 'CF',
    });
  }

  calculateLineSubtotal(index: number): number {
    const line = this.lines.at(index).getRawValue();

    return (
      Number(line.cantidad ?? 0)
      * Number(line.precio_unitario ?? 0)
    );
  }

  invoiceSubtotal(): number {
    return this.lines.controls.reduce(
      (total, control) => {
        const line = control.getRawValue();

        return (
          total
          + Number(line.cantidad ?? 0)
          * Number(line.precio_unitario ?? 0)
        );
      },
      0,
    );
  }

  invoiceDiscount(): number {
    return Number(
      this.invoiceForm.controls
        .descuento.value ?? 0,
    );
  }

  invoiceTotal(): number {
    return Math.max(
      this.invoiceSubtotal()
      - this.invoiceDiscount(),
      0,
    );
  }

  saveInvoice(): void {
    if (this.invoiceForm.invalid) {
      this.invoiceForm.markAllAsTouched();

      this.error.set(
        'Completá correctamente el paciente, '
        + 'los datos de facturación y cada detalle '
        + 'de cobro.',
      );

      return;
    }

    if (this.saving()) {
      return;
    }

    const values =
      this.invoiceForm.getRawValue();

    if (!values.paciente_id) {
      this.error.set(
        'Seleccioná un paciente.',
      );

      return;
    }

    const body: InvoiceCreate = {
      paciente_id:
        Number(values.paciente_id),

      consulta_id:
        values.consulta_id
          ? Number(values.consulta_id)
          : null,

      nit:
        values.nit.trim(),

      nombre_facturacion:
        values.nombre_facturacion.trim(),

      direccion_facturacion:
        values.direccion_facturacion
          .trim() || null,

      descuento:
        Number(values.descuento),

      observaciones:
        values.observaciones.trim() || null,

      items: values.items.map((item) => ({
        tipo_servicio:
          item.tipo_servicio.trim(),

        descripcion:
          item.descripcion.trim(),

        cantidad:
          Number(item.cantidad),

        precio_unitario:
          Number(item.precio_unitario),
      })),
    };

    this.saving.set(true);
    this.error.set('');

    this.api.createInvoice(body).subscribe({
      next: () => {
        this.saving.set(false);

        this.message.set(
          'Factura generada correctamente.',
        );

        this.closeInvoice();
        this.reload();
      },

      error: (error: unknown) => {
        this.saving.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  closeInvoice(): void {
    this.invoiceOpen.set(false);
    this.error.set('');

    this.invoiceForm.reset({
      paciente_id: null,
      consulta_id: null,
      nit: 'CF',
      nombre_facturacion: '',
      direccion_facturacion: '',
      descuento: 0,
      observaciones: '',
    });

    while (this.lines.length > 0) {
      this.lines.removeAt(0);
    }

    this.addLine();
  }

  payment(invoice: Invoice): void {
    this.error.set('');
    this.message.set('');
    this.selected.set(invoice);

    this.paymentForm.reset({
      monto: Number(
        invoice.saldo_pendiente,
      ),
      metodo_pago: 'EFECTIVO',
      referencia: '',
      observaciones: '',
    });

    this.paymentOpen.set(true);
  }

  savePayment(): void {
    if (this.paymentForm.invalid) {
      this.paymentForm.markAllAsTouched();

      this.error.set(
        'Ingresá un monto válido para el pago.',
      );

      return;
    }

    const invoice = this.selected();

    if (!invoice || this.saving()) {
      return;
    }

    const values =
      this.paymentForm.getRawValue();

    const amount = Number(values.monto);

    if (
      amount
      > Number(invoice.saldo_pendiente)
    ) {
      this.error.set(
        'El pago no puede ser mayor '
        + 'que el saldo pendiente.',
      );

      return;
    }

    this.saving.set(true);
    this.error.set('');

    this.api.payInvoice(
      invoice.factura_id,
      amount,
      values.metodo_pago,
      values.referencia.trim() || null,
      values.observaciones.trim() || null,
    ).subscribe({
      next: () => {
        this.saving.set(false);
        this.closePayment();

        this.message.set(
          'Pago aplicado correctamente.',
        );

        this.reload();
      },

      error: (error: unknown) => {
        this.saving.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  closePayment(): void {
    this.paymentOpen.set(false);
    this.selected.set(null);
    this.error.set('');
  }

  cancel(invoice: Invoice): void {
    const reason = prompt(
      'Motivo de anulación:',
      'Factura generada por error',
    );

    const cleanReason = reason?.trim() ?? '';

    if (!cleanReason) {
      return;
    }

    if (cleanReason.length < 3) {
      this.error.set(
        'El motivo debe tener al menos '
        + '3 caracteres.',
      );

      return;
    }

    this.api.cancelInvoice(
      invoice.factura_id,
      cleanReason,
    ).subscribe({
      next: () => {
        this.message.set(
          'Factura anulada correctamente.',
        );

        this.reload();
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });
  }

  protected readonly Number = Number;
}