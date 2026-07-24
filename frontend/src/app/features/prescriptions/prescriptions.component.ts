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
  Medication,
  Prescription,
  PrescriptionCreate,
} from '../../core/models';

@Component({
  selector: 'app-prescriptions',
  imports: [ReactiveFormsModule],
  template: `
    <section class="page-header">
      <div>
        <span class="eyebrow">Farmacia clínica</span>
        <h1>Recetas médicas</h1>
        <p>
          Emití recetas, dispensá medicamentos y controlá
          el estado de cada prescripción.
        </p>
      </div>

      <button
        type="button"
        class="button primary"
        (click)="newPrescription()"
      >
        + Nueva receta
      </button>
    </section>

    @if (message()) {
      <div class="success">
        {{ message() }}
      </div>
    }

    @if (error() && !open()) {
      <div class="alert">
        {{ error() }}
      </div>
    }

    <section class="panel list-panel">
      <div class="filters">
        @for (status of statuses; track status.value) {
          <button
            type="button"
            [class.active]="filter() === status.value"
            (click)="setFilter(status.value)"
          >
            {{ status.label }}
          </button>
        }
      </div>

      @if (loading()) {
        <div class="loading">
          Cargando recetas...
        </div>
      } @else if (items().length > 0) {
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Receta</th>
                <th>Paciente</th>
                <th>Médico</th>
                <th>Medicamentos</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              @for (
                prescription of items();
                track prescription.receta_id
              ) {
                <tr>
                  <td>
                    <strong>
                      #{{ prescription.receta_id }}
                    </strong>

                    <small>
                      Consulta {{ prescription.consulta_id }}
                    </small>
                  </td>

                  <td>
                    <strong>
                      {{ prescription.paciente_nombre }}
                    </strong>

                    <small>
                      {{ prescription.numero_expediente }}
                    </small>
                  </td>

                  <td>
                    {{ prescription.medico_nombre }}
                  </td>

                  <td>
                    {{ prescription.items.length }}
                    medicamento(s)
                  </td>

                  <td>
                    <span
                      class="badge"
                      [attr.data-status]="prescription.estado"
                    >
                      {{ prescription.estado }}
                    </span>
                  </td>

                  <td>
                    <div class="row-actions">
                      @if (prescription.estado === 'EMITIDA') {
                        <button
                          type="button"
                          (click)="dispense(prescription)"
                        >
                          Dispensar
                        </button>

                        <button
                          type="button"
                          class="danger-btn"
                          (click)="cancel(prescription)"
                        >
                          Anular
                        </button>
                      } @else {
                        <span>Sin acciones</span>
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
          <strong>No hay recetas registradas</strong>

          <p>
            Presioná “Nueva receta” para emitir la primera.
          </p>
        </div>
      }
    </section>

    @if (open()) {
      <div
        class="drawer-backdrop"
        (click)="close()"
      >
        <aside
          class="drawer wide"
          (click)="$event.stopPropagation()"
        >
          <div class="drawer-title">
            <div>
              <span class="eyebrow">Prescripción</span>
              <h2>Emitir receta médica</h2>
            </div>

            <button
              type="button"
              aria-label="Cerrar formulario"
              (click)="close()"
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
            [formGroup]="form"
            (ngSubmit)="save()"
          >
            <div class="form-grid">
              <label class="full">
                <span>Consulta clínica *</span>

                <select formControlName="consulta_id">
                  <option [ngValue]="null">
                    Seleccionar consulta
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
                      · {{ consultation.medico_nombre }}
                    </option>
                  }
                </select>

                @if (
                  form.controls.consulta_id.touched
                  && form.controls.consulta_id.invalid
                ) {
                  <small class="field-error">
                    Seleccioná una consulta clínica.
                  </small>
                }
              </label>

              <label class="full">
                <span>Indicaciones generales</span>

                <textarea
                  rows="3"
                  formControlName="indicaciones_generales"
                  placeholder="Ejemplo: Tomar los medicamentos con agua y después de comer."
                ></textarea>
              </label>
            </div>

            <div class="line-heading">
              <div>
                <strong>Medicamentos recetados</strong>
                <small>
                  Completá la dosis, vía, frecuencia y duración.
                </small>
              </div>

              <button
                type="button"
                (click)="addItem()"
              >
                + Agregar medicamento
              </button>
            </div>

            <div
              formArrayName="items"
              class="lines"
            >
              @for (
                group of itemGroups.controls;
                track $index;
                let index = $index
              ) {
                <div
                  class="line"
                  [formGroupName]="index"
                >
                  <div class="line-number">
                    Medicamento {{ index + 1 }}
                  </div>

                  <label class="full">
                    <span>Medicamento *</span>

                    <select formControlName="medicamento_id">
                      <option [ngValue]="null">
                        Seleccionar medicamento
                      </option>

                      @for (
                        medication of medications();
                        track medication.medicamento_id
                      ) {
                        <option
                          [ngValue]="medication.medicamento_id"
                        >
                          {{ medication.nombre }}
                          · {{ medication.presentacion }}
                          · stock {{ medication.stock_actual }}
                        </option>
                      }
                    </select>

                    @if (
                      group.controls.medicamento_id.touched
                      && group.controls.medicamento_id.invalid
                    ) {
                      <small class="field-error">
                        Seleccioná un medicamento.
                      </small>
                    }
                  </label>

                  <label>
                    <span>Dosis *</span>

                    <input
                      formControlName="dosis"
                      placeholder="Ejemplo: 1 tableta"
                    >

                    @if (
                      group.controls.dosis.touched
                      && group.controls.dosis.invalid
                    ) {
                      <small class="field-error">
                        Escribí una dosis, por ejemplo: 1 tableta.
                      </small>
                    }
                  </label>

                  <label>
                    <span>Vía de administración *</span>

                    <input
                      formControlName="via_administracion"
                      placeholder="Ejemplo: Oral"
                    >

                    @if (
                      group.controls.via_administracion.touched
                      && group.controls.via_administracion.invalid
                    ) {
                      <small class="field-error">
                        Debe tener al menos 2 caracteres.
                        Ejemplo: Oral.
                      </small>
                    }
                  </label>

                  <label>
                    <span>Frecuencia *</span>

                    <input
                      formControlName="frecuencia"
                      placeholder="Ejemplo: Cada 8 horas"
                    >

                    @if (
                      group.controls.frecuencia.touched
                      && group.controls.frecuencia.invalid
                    ) {
                      <small class="field-error">
                        No escribás solo “8”. Usá:
                        Cada 8 horas.
                      </small>
                    }
                  </label>

                  <label>
                    <span>Duración *</span>

                    <input
                      formControlName="duracion"
                      placeholder="Ejemplo: 5 días"
                    >

                    @if (
                      group.controls.duracion.touched
                      && group.controls.duracion.invalid
                    ) {
                      <small class="field-error">
                        No escribás solo “5”. Usá:
                        5 días.
                      </small>
                    }
                  </label>

                  <label>
                    <span>Cantidad total *</span>

                    <input
                      type="number"
                      min="1"
                      max="1000"
                      step="1"
                      formControlName="cantidad"
                      placeholder="Ejemplo: 15"
                    >

                    @if (
                      group.controls.cantidad.touched
                      && group.controls.cantidad.invalid
                    ) {
                      <small class="field-error">
                        La cantidad debe estar entre 1 y 1000.
                      </small>
                    }
                  </label>

                  <label class="full">
                    <span>Indicaciones específicas</span>

                    <input
                      formControlName="indicaciones"
                      placeholder="Ejemplo: No exceder la dosis indicada."
                    >
                  </label>

                  <button
                    type="button"
                    class="remove"
                    [disabled]="itemGroups.length === 1"
                    (click)="removeItem(index)"
                  >
                    Quitar medicamento
                  </button>
                </div>
              }
            </div>

            @if (form.invalid && form.touched) {
              <div class="form-warning">
                Revisá los campos marcados. La vía,
                frecuencia y duración deben tener al menos
                2 caracteres.
              </div>
            }

            <div class="actions sticky-actions">
              <button
                type="button"
                class="button secondary"
                (click)="close()"
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
                    ? 'Guardando...'
                    : 'Emitir receta'
                }}
              </button>
            </div>
          </form>
        </aside>
      </div>
    }
  `,
  styles: [`
    .filters {
      display: flex;
      gap: 7px;
      overflow-x: auto;
      padding: 15px;
      border-bottom: 1px solid var(--border);
    }

    .filters button {
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--muted);
      background: #fff;
      font-size: 0.64rem;
      font-weight: 800;
      cursor: pointer;
    }

    .filters button.active {
      border-color: var(--primary);
      color: #fff;
      background: var(--primary);
    }

    .row-actions {
      display: flex;
      align-items: center;
      gap: 6px;
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

    .row-actions span {
      color: #98a2b3;
      font-size: 0.62rem;
    }

    .wide {
      max-width: 900px;
    }

    .drawer-alert {
      margin: 0 0 18px;
    }

    .line-heading {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin: 22px 0 12px;
    }

    .line-heading strong,
    .line-heading small {
      display: block;
    }

    .line-heading strong {
      color: var(--text);
      font-size: 0.85rem;
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

    .lines {
      display: grid;
      gap: 14px;
    }

    .line {
      position: relative;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 13px;
      padding: 18px 15px 15px;
      border: 1px solid var(--border);
      border-radius: 13px;
      background: #fafcff;
    }

    .line-number {
      grid-column: 1 / -1;
      color: var(--primary);
      font-size: 0.67rem;
      font-weight: 900;
      text-transform: uppercase;
    }

    .line label {
      display: grid;
      align-content: start;
      gap: 6px;
    }

    .line label span {
      font-size: 0.65rem;
      font-weight: 800;
    }

    .line input,
    .line select {
      width: 100%;
      min-height: 40px;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 9px;
      outline: none;
      background: white;
    }

    .line input:focus,
    .line select:focus {
      border-color: #84adff;
      box-shadow: 0 0 0 3px rgb(21 94 239 / 9%);
    }

    .line input.ng-invalid.ng-touched,
    .line select.ng-invalid.ng-touched {
      border-color: #f97066;
      background: #fffafa;
    }

    .line .full {
      grid-column: 1 / -1;
    }

    .field-error {
      color: #b42318;
      font-size: 0.61rem;
      line-height: 1.45;
    }

    .remove {
      justify-self: start;
      border: 0;
      color: #b42318;
      background: transparent;
      font-size: 0.65rem;
      font-weight: 800;
      cursor: pointer;
    }

    .remove:disabled {
      color: #98a2b3;
      cursor: not-allowed;
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
      margin: 18px -24px -24px;
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
      font-size: 0.61rem;
    }

    @media (max-width: 700px) {
      .line {
        grid-template-columns: 1fr;
      }

      .line .full,
      .line-number {
        grid-column: auto;
      }

      .line-heading {
        align-items: flex-start;
        flex-direction: column;
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
export class PrescriptionsComponent {
  private readonly api = inject(ApiService);

  readonly items = signal<Prescription[]>([]);
  readonly consultations = signal<Consultation[]>([]);
  readonly medications = signal<Medication[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly open = signal(false);
  readonly filter = signal('');
  readonly error = signal('');
  readonly message = signal('');

  readonly statuses = [
    {
      label: 'Todas',
      value: '',
    },
    {
      label: 'Emitidas',
      value: 'EMITIDA',
    },
    {
      label: 'Dispensadas',
      value: 'DISPENSADA',
    },
    {
      label: 'Anuladas',
      value: 'ANULADA',
    },
  ];

  readonly form = new FormGroup({
    consulta_id: new FormControl<number | null>(
      null,
      Validators.required,
    ),

    indicaciones_generales: new FormControl(
      '',
      {
        nonNullable: true,
        validators: [
          Validators.maxLength(1500),
        ],
      },
    ),

    items: new FormArray([
      this.createItemGroup(),
    ]),
  });

  get itemGroups() {
    return this.form.controls.items;
  }

  constructor() {
    this.load();

    this.api.consultations().subscribe({
      next: (response) => {
        this.consultations.set(response.items);
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });

    this.api.medications().subscribe({
      next: (response) => {
        this.medications.set(
          response.items.filter(
            (medication) =>
              medication.activo
              && medication.stock_actual > 0,
          ),
        );
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });
  }

  createItemGroup() {
    return new FormGroup({
      medicamento_id: new FormControl<number | null>(
        null,
        Validators.required,
      ),

      dosis: new FormControl('', {
        nonNullable: true,
        validators: [
          Validators.required,
          Validators.minLength(1),
          Validators.maxLength(100),
        ],
      }),

      via_administracion: new FormControl(
        'Oral',
        {
          nonNullable: true,
          validators: [
            Validators.required,
            Validators.minLength(2),
            Validators.maxLength(80),
          ],
        },
      ),

      frecuencia: new FormControl('', {
        nonNullable: true,
        validators: [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(100),
        ],
      }),

      duracion: new FormControl('', {
        nonNullable: true,
        validators: [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(100),
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

      indicaciones: new FormControl('', {
        nonNullable: true,
        validators: [
          Validators.maxLength(1000),
        ],
      }),
    });
  }

  newPrescription(): void {
    this.error.set('');
    this.message.set('');

    this.form.reset({
      consulta_id: null,
      indicaciones_generales: '',
    });

    while (this.itemGroups.length > 0) {
      this.itemGroups.removeAt(0);
    }

    this.addItem();
    this.open.set(true);
  }

  addItem(): void {
    this.itemGroups.push(
      this.createItemGroup(),
    );
  }

  removeItem(index: number): void {
    if (this.itemGroups.length > 1) {
      this.itemGroups.removeAt(index);
    }
  }

  load(): void {
    this.loading.set(true);
    this.error.set('');

    this.api.prescriptions(
      this.filter(),
    ).subscribe({
      next: (response) => {
        this.items.set(response.items);
        this.loading.set(false);
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
        this.loading.set(false);
      },
    });
  }

  setFilter(value: string): void {
    this.filter.set(value);
    this.load();
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();

      this.error.set(
        'Revisá la receta. La vía, frecuencia y duración '
        + 'deben tener al menos 2 caracteres.',
      );

      return;
    }

    if (this.saving()) {
      return;
    }

    this.saving.set(true);
    this.error.set('');

    const values = this.form.getRawValue();

    const body: PrescriptionCreate = {
      consulta_id: Number(
        values.consulta_id,
      ),

      indicaciones_generales:
        values.indicaciones_generales
          .trim() || null,

      items: values.items.map((item) => ({
        medicamento_id: Number(
          item.medicamento_id,
        ),

        dosis: item.dosis.trim(),

        via_administracion:
          item.via_administracion.trim(),

        frecuencia:
          item.frecuencia.trim(),

        duracion:
          item.duracion.trim(),

        cantidad: Number(item.cantidad),

        indicaciones:
          item.indicaciones.trim() || null,
      })),
    };

    this.api.createPrescription(body).subscribe({
      next: () => {
        this.saving.set(false);

        this.message.set(
          'Receta emitida correctamente.',
        );

        this.close();
        this.load();
      },

      error: (error: unknown) => {
        this.saving.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  dispense(prescription: Prescription): void {
    const confirmed = confirm(
      `¿Dispensar la receta #${prescription.receta_id}? `
      + 'Se descontará el inventario.',
    );

    if (!confirmed) {
      return;
    }

    this.error.set('');

    this.api.dispensePrescription(
      prescription.receta_id,
    ).subscribe({
      next: () => {
        this.message.set(
          'Receta dispensada e inventario actualizado.',
        );

        this.load();
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });
  }

  cancel(prescription: Prescription): void {
    const reason = prompt(
      'Motivo de anulación:',
      'Error en la prescripción',
    );

    const cleanReason = reason?.trim() ?? '';

    if (!cleanReason) {
      return;
    }

    if (cleanReason.length < 3) {
      this.error.set(
        'El motivo de anulación debe tener '
        + 'al menos 3 caracteres.',
      );

      return;
    }

    this.api.cancelPrescription(
      prescription.receta_id,
      cleanReason,
    ).subscribe({
      next: () => {
        this.message.set(
          'Receta anulada correctamente.',
        );

        this.load();
      },

      error: (error: unknown) => {
        this.error.set(apiError(error));
      },
    });
  }

  close(): void {
    this.open.set(false);
    this.error.set('');

    this.form.reset({
      consulta_id: null,
      indicaciones_generales: '',
    });

    while (this.itemGroups.length > 0) {
      this.itemGroups.removeAt(0);
    }

    this.addItem();
  }
}