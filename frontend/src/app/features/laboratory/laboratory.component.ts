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
  Consultation,
  LabOrder,
  LabOrderCreate,
  LabOrderItem,
  LabTestPayload,
  LabTestType,
} from '../../core/models';

@Component({
  selector: 'app-laboratory',
  imports: [ReactiveFormsModule],
  template: `
    <section class="page-header">
      <div>
        <span class="eyebrow">Apoyo diagnóstico</span>
        <h1>Laboratorio clínico</h1>
        <p>Tipos de examen, órdenes y resultados.</p>
      </div>

      <div class="head-actions">
        <button
          type="button"
          class="button secondary"
          (click)="openTestForm()"
        >
          + Tipo de examen
        </button>

        <button
          type="button"
          class="button primary"
          (click)="openOrderForm()"
        >
          + Nueva orden
        </button>
      </div>
    </section>

    @if (message()) {
      <div class="success">{{ message() }}</div>
    }

    @if (
      error()
      && !testOpen()
      && !orderOpen()
      && !resultOpen()
    ) {
      <div class="alert">{{ error() }}</div>
    }

    <div class="tabs">
      <button
        type="button"
        [class.active]="tab() === 'orders'"
        (click)="tab.set('orders')"
      >
        Órdenes
      </button>
      <button
        type="button"
        [class.active]="tab() === 'tests'"
        (click)="tab.set('tests')"
      >
        Tipos de examen
      </button>
    </div>

    @if (tab() === 'orders') {
      <section class="panel list-panel">
        @if (ordersLoading()) {
          <div class="loading">Cargando órdenes...</div>
        } @else if (orders().length > 0) {
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Orden</th>
                  <th>Paciente</th>
                  <th>Médico</th>
                  <th>Exámenes</th>
                  <th>Total</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                @for (
                  order of orders();
                  track order.orden_laboratorio_id
                ) {
                  <tr>
                    <td>
                      <strong>#{{ order.orden_laboratorio_id }}</strong>
                      <small>Consulta #{{ order.consulta_id }}</small>
                    </td>
                    <td>
                      <strong>{{ order.paciente_nombre }}</strong>
                      <small>{{ order.numero_expediente }}</small>
                    </td>
                    <td>{{ order.medico_nombre }}</td>
                    <td>{{ order.items.length }}</td>
                    <td>Q {{ money(order.total_estimado) }}</td>
                    <td>
                      <span
                        class="badge"
                        [attr.data-status]="order.estado"
                      >
                        {{ order.estado.replaceAll('_', ' ') }}
                      </span>
                    </td>
                    <td>
                      <div class="row-actions">
                        @if (order.estado === 'SOLICITADA') {
                          <button
                            type="button"
                            (click)="processOrder(order)"
                          >
                            Procesar
                          </button>
                        }

                        @for (
                          item of order.items;
                          track item.detalle_orden_id
                        ) {
                          @if (
                            item.estado !== 'COMPLETADO'
                            && order.estado !== 'CANCELADA'
                          ) {
                            <button
                              type="button"
                              (click)="openResultForm(order, item)"
                            >
                              Resultado
                            </button>
                          }
                        }

                        @if (
                          order.estado !== 'COMPLETADA'
                          && order.estado !== 'CANCELADA'
                        ) {
                          <button
                            type="button"
                            class="danger-btn"
                            (click)="cancelOrder(order)"
                          >
                            Cancelar
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
            <strong>No hay órdenes de laboratorio</strong>
            <p>Creá la primera orden desde “Nueva orden”.</p>
          </div>
        }
      </section>
    } @else {
      @if (testsLoading()) {
        <div class="loading">Cargando tipos de examen...</div>
      } @else if (activeTests().length > 0) {
        <section class="test-grid">
          @for (
            test of activeTests();
            track test.tipo_examen_id
          ) {
            <article>
              <small>{{ test.codigo }}</small>
              <h2>{{ test.nombre }}</h2>
              <p>{{ test.descripcion || 'Sin descripción.' }}</p>

              <dl>
                <div>
                  <dt>Muestra</dt>
                  <dd>{{ test.muestra_requerida }}</dd>
                </div>
                <div>
                  <dt>Tiempo</dt>
                  <dd>{{ test.tiempo_estimado_horas }} h</dd>
                </div>
                <div>
                  <dt>Precio</dt>
                  <dd>Q {{ money(test.precio) }}</dd>
                </div>
              </dl>

              <button
                type="button"
                (click)="editTest(test)"
              >
                Editar
              </button>
            </article>
          }
        </section>
      } @else {
        <section class="panel list-panel">
          <div class="empty">
            <strong>No hay tipos de examen</strong>
            <p>Registrá uno con “Tipo de examen”.</p>
          </div>
        </section>
      }
    }

    @if (testOpen()) {
      <div class="drawer-backdrop" (click)="closeTestForm()">
        <aside class="drawer" (click)="$event.stopPropagation()">
          <div class="drawer-title">
            <div>
              <span class="eyebrow">Catálogo</span>
              <h2>
                {{ selectedTest() ? 'Editar examen' : 'Nuevo examen' }}
              </h2>
            </div>
            <button type="button" (click)="closeTestForm()">×</button>
          </div>

          @if (error()) {
            <div class="alert drawer-alert">{{ error() }}</div>
          }

          <form
            class="form-grid"
            [formGroup]="testForm"
            (ngSubmit)="saveTest()"
          >
            <label>
              <span>Código *</span>
              <input
                formControlName="codigo"
                placeholder="Ejemplo: HEM-001"
                [readonly]="!!selectedTest()"
              >
            </label>

            <label>
              <span>Nombre *</span>
              <input
                formControlName="nombre"
                placeholder="Ejemplo: Hemograma completo"
              >
            </label>

            <label>
              <span>Muestra requerida *</span>
              <input
                formControlName="muestra_requerida"
                placeholder="Ejemplo: Sangre venosa"
              >
            </label>

            <label>
              <span>Tiempo estimado (horas) *</span>
              <input
                type="number"
                min="1"
                max="720"
                formControlName="tiempo_estimado_horas"
                placeholder="24"
              >
            </label>

            <label class="full">
              <span>Precio *</span>
              <input
                type="number"
                min="0"
                step="0.01"
                formControlName="precio"
                placeholder="75.00"
              >
            </label>

            <label class="full">
              <span>Descripción</span>
              <textarea
                rows="3"
                formControlName="descripcion"
                placeholder="Ejemplo: Evalúa las células de la sangre."
              ></textarea>
            </label>

            @if (testForm.invalid && testForm.touched) {
              <div class="form-warning full">
                Código: mínimo 2 caracteres. Nombre: mínimo 3.
                Muestra: mínimo 2. Tiempo: 1 a 720 horas.
              </div>
            }

            <div class="actions full sticky-actions">
              <button
                type="button"
                class="button secondary"
                (click)="closeTestForm()"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="button primary"
                [disabled]="savingTest()"
              >
                {{ savingTest() ? 'Guardando...' : 'Guardar examen' }}
              </button>
            </div>
          </form>
        </aside>
      </div>
    }

    @if (orderOpen()) {
      <div class="drawer-backdrop" (click)="closeOrderForm()">
        <aside class="drawer wide" (click)="$event.stopPropagation()">
          <div class="drawer-title">
            <div>
              <span class="eyebrow">Laboratorio</span>
              <h2>Nueva orden</h2>
            </div>
            <button type="button" (click)="closeOrderForm()">×</button>
          </div>

          @if (error()) {
            <div class="alert drawer-alert">{{ error() }}</div>
          }

          <form [formGroup]="orderForm" (ngSubmit)="saveOrder()">
            <div class="form-grid">
              <label class="full">
                <span>Consulta clínica *</span>

                @if (consultationsLoading()) {
                  <select disabled>
                    <option>Cargando consultas...</option>
                  </select>
                } @else {
                  <select formControlName="consulta_id">
                    <option [ngValue]="null">
                      Seleccionar consulta
                    </option>
                    @for (
                      consultation of consultations();
                      track consultation.consulta_id
                    ) {
                      <option [ngValue]="consultation.consulta_id">
                        #{{ consultation.consulta_id }} ·
                        {{ consultation.paciente_nombre }} ·
                        Dr. {{ consultation.medico_nombre }}
                      </option>
                    }
                  </select>
                }

                @if (
                  !consultationsLoading()
                  && consultations().length === 0
                ) {
                  <small class="field-error">
                    No hay consultas clínicas. Una cita sola no basta:
                    primero registrá la consulta en el módulo Consultas.
                  </small>
                }
              </label>

              <label>
                <span>Prioridad *</span>
                <select formControlName="prioridad">
                  <option value="NORMAL">Normal</option>
                  <option value="URGENTE">Urgente</option>
                </select>
              </label>

              <label>
                <span>Indicaciones</span>
                <input
                  formControlName="indicaciones"
                  placeholder="Ejemplo: Realizar en ayunas"
                >
              </label>
            </div>

            <div class="line-heading">
              <div>
                <strong>Exámenes solicitados</strong>
                <small>Podés agregar más de uno.</small>
              </div>
              <button type="button" (click)="addOrderItem()">
                + Agregar examen
              </button>
            </div>

            @if (activeTests().length === 0) {
              <div class="form-warning">
                No hay tipos de examen activos. Registrá uno primero.
              </div>
            }

            <div formArrayName="items" class="order-lines">
              @for (
                group of orderItems.controls;
                track $index;
                let index = $index
              ) {
                <div class="order-line" [formGroupName]="index">
                  <label>
                    <span>Tipo de examen *</span>
                    <select formControlName="tipo_examen_id">
                      <option [ngValue]="null">
                        Seleccionar examen
                      </option>
                      @for (
                        test of activeTests();
                        track test.tipo_examen_id
                      ) {
                        <option [ngValue]="test.tipo_examen_id">
                          {{ test.codigo }} · {{ test.nombre }} ·
                          Q {{ money(test.precio) }}
                        </option>
                      }
                    </select>
                  </label>

                  <label>
                    <span>Observaciones</span>
                    <input
                      formControlName="observaciones"
                      placeholder="Ejemplo: Tomar muestra sanguínea"
                    >
                  </label>

                  <button
                    type="button"
                    class="remove-line"
                    [disabled]="orderItems.length === 1"
                    (click)="removeOrderItem(index)"
                  >
                    Quitar
                  </button>
                </div>
              }
            </div>

            @if (orderForm.invalid && orderForm.touched) {
              <div class="form-warning">
                Seleccioná una consulta y un tipo de examen en cada fila.
              </div>
            }

            <div class="actions sticky-actions">
              <button
                type="button"
                class="button secondary"
                (click)="closeOrderForm()"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="button primary"
                [disabled]="
                  savingOrder()
                  || consultationsLoading()
                  || activeTests().length === 0
                "
              >
                {{ savingOrder() ? 'Guardando...' : 'Crear orden' }}
              </button>
            </div>
          </form>
        </aside>
      </div>
    }

    @if (
      resultOpen()
      && selectedOrder()
      && selectedItem()
    ) {
      <div class="drawer-backdrop" (click)="closeResultForm()">
        <aside class="drawer" (click)="$event.stopPropagation()">
          <div class="drawer-title">
            <div>
              <span class="eyebrow">Resultado</span>
              <h2>{{ selectedItem()!.nombre_examen }}</h2>
            </div>
            <button type="button" (click)="closeResultForm()">×</button>
          </div>

          @if (error()) {
            <div class="alert drawer-alert">{{ error() }}</div>
          }

          <form
            class="form-grid"
            [formGroup]="resultForm"
            (ngSubmit)="saveResult()"
          >
            <label class="full">
              <span>Resultado *</span>
              <textarea
                rows="4"
                formControlName="resultado"
                placeholder="Ejemplo: Hemoglobina 14.5 g/dL"
              ></textarea>
            </label>

            <label class="full">
              <span>Valores de referencia</span>
              <textarea
                rows="2"
                formControlName="valores_referencia"
                placeholder="Ejemplo: 13.0 a 17.0 g/dL"
              ></textarea>
            </label>

            <label class="full">
              <span>Interpretación</span>
              <textarea
                rows="3"
                formControlName="interpretacion"
                placeholder="Ejemplo: Dentro del rango normal"
              ></textarea>
            </label>

            <label class="full">
              <span>URL del archivo</span>
              <input
                formControlName="archivo_url"
                placeholder="Ejemplo: https://servidor/resultado.pdf"
              >
            </label>

            <div class="actions full sticky-actions">
              <button
                type="button"
                class="button secondary"
                (click)="closeResultForm()"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="button primary"
                [disabled]="savingResult()"
              >
                {{
                  savingResult()
                    ? 'Guardando...'
                    : 'Guardar resultado'
                }}
              </button>
            </div>
          </form>
        </aside>
      </div>
    }
  `,
  styles: [`
    .head-actions,
    .tabs,
    .row-actions,
    .actions {
      display: flex;
      gap: 8px;
    }

    .tabs {
      margin: 20px 0 12px;
    }

    .tabs button {
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 13px;
      color: var(--muted);
      background: #fff;
      font-size: .66rem;
      font-weight: 800;
      cursor: pointer;
    }

    .tabs button.active {
      color: #fff;
      background: var(--primary);
    }

    .row-actions {
      flex-wrap: wrap;
    }

    .row-actions button {
      border: 0;
      border-radius: 7px;
      padding: 5px 7px;
      color: #175cd3;
      background: #eaf2ff;
      font-size: .57rem;
      font-weight: 800;
      cursor: pointer;
    }

    .row-actions .danger-btn {
      color: #b42318;
      background: #feeceb;
    }

    .test-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 15px;
    }

    .test-grid article {
      padding: 18px;
      border: 1px solid var(--border);
      border-radius: 16px;
      background: #fff;
      box-shadow: var(--shadow);
    }

    .test-grid small {
      color: var(--primary);
      font-weight: 900;
    }

    .test-grid h2 {
      margin: 6px 0;
      font-size: .92rem;
    }

    .test-grid p {
      min-height: 38px;
      margin: 0;
      color: var(--muted);
      font-size: .68rem;
    }

    .test-grid dl {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin: 15px 0;
    }

    .test-grid dt {
      color: #98a2b3;
      font-size: .58rem;
    }

    .test-grid dd {
      margin: 3px 0 0;
      font-size: .67rem;
      font-weight: 800;
    }

    .test-grid article > button,
    .line-heading button {
      border: 0;
      color: var(--primary);
      background: transparent;
      font-size: .65rem;
      font-weight: 800;
      cursor: pointer;
    }

    .wide {
      max-width: 860px;
    }

    .drawer-alert {
      margin: 0 0 18px;
    }

    .line-heading {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 22px 0 10px;
    }

    .line-heading strong,
    .line-heading small,
    table strong,
    table small {
      display: block;
    }

    .line-heading small,
    table small {
      margin-top: 4px;
      color: #98a2b3;
      font-size: .61rem;
    }

    .order-lines {
      display: grid;
      gap: 10px;
    }

    .order-line {
      display: grid;
      grid-template-columns: 1fr 1fr auto;
      gap: 9px;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 11px;
      background: #fafcff;
    }

    .order-line label {
      display: grid;
      gap: 6px;
    }

    .order-line label span {
      font-size: .63rem;
      font-weight: 800;
    }

    .order-line select,
    .order-line input {
      min-height: 40px;
      padding: 8px;
      border: 1px solid var(--border);
      border-radius: 9px;
      background: #fff;
    }

    .remove-line {
      align-self: end;
      min-height: 40px;
      border: 0;
      color: #b42318;
      background: transparent;
      font-size: .62rem;
      font-weight: 900;
      cursor: pointer;
    }

    .field-error {
      color: #b42318 !important;
      font-size: .61rem !important;
      line-height: 1.45;
    }

    .form-warning {
      margin-top: 12px;
      padding: 11px 13px;
      border: 1px solid #fedf89;
      border-radius: 10px;
      color: #93370d;
      background: #fffaeb;
      font-size: .69rem;
      line-height: 1.5;
    }

    .sticky-actions {
      position: sticky;
      z-index: 5;
      bottom: -24px;
      justify-content: flex-end;
      margin: 18px -24px -24px;
      padding: 15px 24px;
      border-top: 1px solid var(--border);
      background: #fff;
    }

    @media (max-width: 700px) {
      .head-actions {
        width: 100%;
        display: grid;
      }

      .line-heading {
        align-items: flex-start;
        flex-direction: column;
      }

      .order-line {
        grid-template-columns: 1fr;
      }

      .sticky-actions {
        bottom: -20px;
        margin: 18px -16px -20px;
        padding: 14px 16px;
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LaboratoryComponent {
  private readonly api = inject(ApiService);

  readonly tab = signal<'orders' | 'tests'>('orders');
  readonly tests = signal<LabTestType[]>([]);
  readonly orders = signal<LabOrder[]>([]);
  readonly consultations = signal<Consultation[]>([]);

  readonly ordersLoading = signal(true);
  readonly testsLoading = signal(true);
  readonly consultationsLoading = signal(true);
  readonly savingTest = signal(false);
  readonly savingOrder = signal(false);
  readonly savingResult = signal(false);

  readonly testOpen = signal(false);
  readonly orderOpen = signal(false);
  readonly resultOpen = signal(false);

  readonly selectedTest = signal<LabTestType | null>(null);
  readonly selectedOrder = signal<LabOrder | null>(null);
  readonly selectedItem = signal<LabOrderItem | null>(null);

  readonly error = signal('');
  readonly message = signal('');

  readonly testForm = new FormGroup({
    codigo: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(30),
      ],
    }),
    nombre: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.minLength(3),
        Validators.maxLength(150),
      ],
    }),
    descripcion: new FormControl('', {
      nonNullable: true,
      validators: [Validators.maxLength(500)],
    }),
    muestra_requerida: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(100),
      ],
    }),
    tiempo_estimado_horas: new FormControl(24, {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.min(1),
        Validators.max(720),
      ],
    }),
    precio: new FormControl(0, {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.min(0),
      ],
    }),
  });

  readonly orderForm = new FormGroup({
    consulta_id: new FormControl<number | null>(
      null,
      Validators.required,
    ),
    indicaciones: new FormControl('', {
      nonNullable: true,
      validators: [Validators.maxLength(1000)],
    }),
    prioridad: new FormControl('NORMAL', {
      nonNullable: true,
      validators: [Validators.required],
    }),
    items: new FormArray([
      this.createOrderItemGroup(),
    ]),
  });

  readonly resultForm = new FormGroup({
    resultado: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(3000),
      ],
    }),
    valores_referencia: new FormControl('', {
      nonNullable: true,
      validators: [Validators.maxLength(1000)],
    }),
    interpretacion: new FormControl('', {
      nonNullable: true,
      validators: [Validators.maxLength(1500)],
    }),
    archivo_url: new FormControl('', {
      nonNullable: true,
      validators: [Validators.maxLength(500)],
    }),
  });

  get orderItems() {
    return this.orderForm.controls.items;
  }

  constructor() {
    this.reloadAll();
  }

  activeTests(): LabTestType[] {
    return this.tests().filter((test) => test.activo);
  }

  createOrderItemGroup() {
    return new FormGroup({
      tipo_examen_id: new FormControl<number | null>(
        null,
        Validators.required,
      ),
      observaciones: new FormControl('', {
        nonNullable: true,
        validators: [Validators.maxLength(500)],
      }),
    });
  }

  reloadAll(): void {
    this.loadTests();
    this.loadConsultations();
    this.loadOrders();
  }

  loadTests(): void {
    this.testsLoading.set(true);

    this.api.labTests().subscribe({
      next: (tests) => {
        this.tests.set(tests);
        this.testsLoading.set(false);
      },
      error: (error: unknown) => {
        this.tests.set([]);
        this.testsLoading.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  loadConsultations(): void {
    this.consultationsLoading.set(true);

    this.api.consultations().subscribe({
      next: (response) => {
        this.consultations.set(response.items);
        this.consultationsLoading.set(false);
      },
      error: (error: unknown) => {
        this.consultations.set([]);
        this.consultationsLoading.set(false);
        this.error.set(
          `No se pudieron cargar las consultas: ${apiError(error)}`,
        );
      },
    });
  }

  loadOrders(): void {
    this.ordersLoading.set(true);

    this.api.labOrders().subscribe({
      next: (response) => {
        this.orders.set(response.items);
        this.ordersLoading.set(false);
      },
      error: (error: unknown) => {
        this.orders.set([]);
        this.ordersLoading.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  openTestForm(): void {
    this.error.set('');
    this.message.set('');
    this.selectedTest.set(null);
    this.testForm.reset({
      codigo: '',
      nombre: '',
      descripcion: '',
      muestra_requerida: '',
      tiempo_estimado_horas: 24,
      precio: 0,
    });
    this.testOpen.set(true);
  }

  editTest(test: LabTestType): void {
    this.error.set('');
    this.selectedTest.set(test);
    this.testForm.reset({
      codigo: test.codigo,
      nombre: test.nombre,
      descripcion: test.descripcion ?? '',
      muestra_requerida: test.muestra_requerida,
      tiempo_estimado_horas: test.tiempo_estimado_horas,
      precio: Number(test.precio),
    });
    this.testOpen.set(true);
  }

  saveTest(): void {
    if (this.testForm.invalid) {
      this.testForm.markAllAsTouched();
      this.error.set(
        'Revisá los campos: código mínimo 2, nombre mínimo 3 '
        + 'y muestra mínimo 2 caracteres.',
      );
      return;
    }

    if (this.savingTest()) {
      return;
    }

    this.savingTest.set(true);
    this.error.set('');

    const values = this.testForm.getRawValue();
    const selected = this.selectedTest();
    const payload: LabTestPayload = {
      nombre: values.nombre.trim(),
      descripcion: values.descripcion.trim() || null,
      muestra_requerida: values.muestra_requerida.trim(),
      tiempo_estimado_horas: Number(values.tiempo_estimado_horas),
      precio: Number(values.precio),
    };

    const request = selected
      ? this.api.updateLabTest(selected.tipo_examen_id, payload)
      : this.api.createLabTest({
          ...payload,
          codigo: values.codigo.trim().toUpperCase(),
        });

    request.subscribe({
      next: () => {
        this.savingTest.set(false);
        this.closeTestForm();
        this.message.set(
          selected
            ? 'Tipo de examen actualizado.'
            : 'Tipo de examen registrado.',
        );
        this.loadTests();
        this.tab.set('tests');
      },
      error: (error: unknown) => {
        this.savingTest.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  closeTestForm(): void {
    this.testOpen.set(false);
    this.selectedTest.set(null);
    this.error.set('');
  }

  openOrderForm(): void {
    this.error.set('');
    this.message.set('');
    this.loadConsultations();
    this.loadTests();

    this.orderForm.controls.consulta_id.setValue(null);
    this.orderForm.controls.indicaciones.setValue('');
    this.orderForm.controls.prioridad.setValue('NORMAL');

    while (this.orderItems.length > 0) {
      this.orderItems.removeAt(0);
    }
    this.orderItems.push(this.createOrderItemGroup());

    this.orderOpen.set(true);
  }

  addOrderItem(): void {
    this.orderItems.push(this.createOrderItemGroup());
  }

  removeOrderItem(index: number): void {
    if (this.orderItems.length > 1) {
      this.orderItems.removeAt(index);
    }
  }

  saveOrder(): void {
    if (this.orderForm.invalid) {
      this.orderForm.markAllAsTouched();
      this.error.set(
        'Seleccioná una consulta y un examen en cada fila.',
      );
      return;
    }

    if (this.savingOrder()) {
      return;
    }

    const values = this.orderForm.getRawValue();
    const testIds = values.items.map(
      (item) => Number(item.tipo_examen_id),
    );

    if (new Set(testIds).size !== testIds.length) {
      this.error.set(
        'No podés repetir el mismo examen en una orden.',
      );
      return;
    }

    this.savingOrder.set(true);
    this.error.set('');

    const payload: LabOrderCreate = {
      consulta_id: Number(values.consulta_id),
      indicaciones: values.indicaciones.trim() || null,
      prioridad: values.prioridad,
      items: values.items.map((item) => ({
        tipo_examen_id: Number(item.tipo_examen_id),
        observaciones: item.observaciones.trim() || null,
      })),
    };

    this.api.createLabOrder(payload).subscribe({
      next: () => {
        this.savingOrder.set(false);
        this.closeOrderForm();
        this.message.set('Orden de laboratorio creada.');
        this.loadOrders();
        this.tab.set('orders');
      },
      error: (error: unknown) => {
        this.savingOrder.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  closeOrderForm(): void {
    this.orderOpen.set(false);
    this.error.set('');
  }

  openResultForm(order: LabOrder, item: LabOrderItem): void {
    this.error.set('');
    this.selectedOrder.set(order);
    this.selectedItem.set(item);
    this.resultForm.reset({
      resultado: item.resultado?.resultado ?? '',
      valores_referencia:
        item.resultado?.valores_referencia ?? '',
      interpretacion: item.resultado?.interpretacion ?? '',
      archivo_url: item.resultado?.archivo_url ?? '',
    });
    this.resultOpen.set(true);
  }

  saveResult(): void {
    if (this.resultForm.invalid) {
      this.resultForm.markAllAsTouched();
      this.error.set(
        'El resultado debe tener al menos 2 caracteres.',
      );
      return;
    }

    const order = this.selectedOrder();
    const item = this.selectedItem();

    if (!order || !item || this.savingResult()) {
      return;
    }

    this.savingResult.set(true);
    this.error.set('');
    const values = this.resultForm.getRawValue();

    this.api.saveLabResult(
      order.orden_laboratorio_id,
      item.detalle_orden_id,
      {
        resultado: values.resultado.trim(),
        valores_referencia:
          values.valores_referencia.trim() || null,
        interpretacion: values.interpretacion.trim() || null,
        archivo_url: values.archivo_url.trim() || null,
      },
    ).subscribe({
      next: () => {
        this.savingResult.set(false);
        this.closeResultForm();
        this.message.set('Resultado registrado.');
        this.loadOrders();
      },
      error: (error: unknown) => {
        this.savingResult.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  closeResultForm(): void {
    this.resultOpen.set(false);
    this.selectedOrder.set(null);
    this.selectedItem.set(null);
    this.error.set('');
  }

  processOrder(order: LabOrder): void {
    this.api.updateLabOrderStatus(
      order.orden_laboratorio_id,
      'EN_PROCESO',
    ).subscribe({
      next: () => {
        this.message.set('La orden cambió a EN PROCESO.');
        this.loadOrders();
      },
      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });
  }

  cancelOrder(order: LabOrder): void {
    const reason = prompt(
      'Motivo de cancelación:',
      'Orden cancelada por solicitud médica',
    );
    const cleanReason = reason?.trim() ?? '';

    if (!cleanReason) {
      return;
    }

    this.api.updateLabOrderStatus(
      order.orden_laboratorio_id,
      'CANCELADA',
      cleanReason,
    ).subscribe({
      next: () => {
        this.message.set('Orden cancelada.');
        this.loadOrders();
      },
      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });
  }

  money(value: number | string | null | undefined): string {
    return Number(value ?? 0).toFixed(2);
  }
}
