import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';

import { ApiService } from '../../core/api.service';
import { apiError } from '../../core/api-error';
import {
  Medication,
  MedicationPayload,
} from '../../core/models';

@Component({
  selector: 'app-medications',
  imports: [ReactiveFormsModule],
  template: `
    <section class="page-header">
      <div>
        <span class="eyebrow">Farmacia</span>
        <h1>Medicamentos e inventario</h1>
        <p>
          Catálogo, precios, stock mínimo y movimientos de inventario.
        </p>
      </div>

      <button
        type="button"
        class="button primary"
        (click)="newMedication()"
      >
        + Nuevo medicamento
      </button>
    </section>

    @if (message()) {
      <div class="success">{{ message() }}</div>
    }

    @if (error() && !open() && !stockOpen()) {
      <div class="alert">{{ error() }}</div>
    }

    <section class="panel list-panel">
      <div class="toolbar">
        <input
          #searchInput
          type="search"
          placeholder="Buscar código o medicamento"
          (keyup.enter)="load(searchInput.value)"
        >

        <label class="check">
          <input
            type="checkbox"
            (change)="toggleLow($event)"
          >
          Solo stock bajo
        </label>

        <button
          type="button"
          class="button secondary"
          (click)="load(searchInput.value)"
        >
          Buscar
        </button>
      </div>

      @if (loading()) {
        <div class="loading">
          Cargando medicamentos...
        </div>
      } @else if (items().length > 0) {
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Medicamento</th>
                <th>Presentación</th>
                <th>Stock</th>
                <th>Precio</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              @for (
                medication of items();
                track medication.medicamento_id
              ) {
                <tr>
                  <td>
                    <strong>
                      {{ medication.codigo }}
                    </strong>
                  </td>

                  <td>
                    <strong>
                      {{ medication.nombre }}
                    </strong>
                  </td>

                  <td>
                    {{ medication.presentacion }} ·
                    {{ medication.unidad }}
                  </td>

                  <td>
                    <strong
                      [class.danger]="medication.stock_bajo"
                    >
                      {{ medication.stock_actual }}
                    </strong>

                    <small>
                      Mínimo {{ medication.stock_minimo }}
                    </small>
                  </td>

                  <td>
                    Q {{ formatPrice(medication.precio_unitario) }}
                  </td>

                  <td>
                    <span
                      class="badge"
                      [attr.data-status]="
                        medication.stock_bajo
                          ? 'PENDIENTE'
                          : 'ACTIVO'
                      "
                    >
                      {{
                        medication.stock_bajo
                          ? 'Stock bajo'
                          : 'Disponible'
                      }}
                    </span>
                  </td>

                  <td>
                    <div class="row-actions">
                      <button
                        type="button"
                        (click)="edit(medication)"
                      >
                        Editar
                      </button>

                      <button
                        type="button"
                        (click)="stock(medication)"
                      >
                        Stock
                      </button>
                    </div>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      } @else {
        <div class="empty">
          <strong>
            No hay medicamentos registrados
          </strong>

          <p>
            Presioná “Nuevo medicamento” para agregar
            el primero.
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
          class="drawer"
          (click)="$event.stopPropagation()"
        >
          <div class="drawer-title">
            <div>
              <span class="eyebrow">Farmacia</span>

              <h2>
                {{
                  selected()
                    ? 'Editar medicamento'
                    : 'Nuevo medicamento'
                }}
              </h2>
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
            class="form-grid"
            [formGroup]="form"
            (ngSubmit)="save()"
          >
            <label>
              <span>Código *</span>

              <input
                formControlName="codigo"
                placeholder="Ejemplo: MED-004"
                [readonly]="!!selected()"
              >
            </label>

            <label>
              <span>Nombre *</span>

              <input
                formControlName="nombre"
                placeholder="Ejemplo: Aspirina"
              >
            </label>

            <label>
              <span>Presentación *</span>

              <input
                formControlName="presentacion"
                placeholder="Ejemplo: Tabletas"
              >
            </label>

            <label>
              <span>Unidad *</span>

              <select formControlName="unidad">
                <option value="UNIDAD">
                  Unidad
                </option>

                <option value="TABLETA">
                  Tableta
                </option>

                <option value="CAPSULA">
                  Cápsula
                </option>

                <option value="FRASCO">
                  Frasco
                </option>

                <option value="AMPOLLA">
                  Ampolla
                </option>

                <option value="ML">
                  Mililitro
                </option>
              </select>
            </label>

            <label>
              <span>Stock actual *</span>

              <input
                type="number"
                min="0"
                step="1"
                formControlName="stock_actual"
                [readonly]="!!selected()"
              >

              @if (selected()) {
                <small>
                  Para cambiarlo, utilizá el botón Stock.
                </small>
              }
            </label>

            <label>
              <span>Stock mínimo *</span>

              <input
                type="number"
                min="0"
                step="1"
                formControlName="stock_minimo"
              >
            </label>

            <label class="full">
              <span>Precio unitario *</span>

              <input
                type="number"
                min="0"
                step="0.01"
                formControlName="precio_unitario"
                placeholder="0.00"
              >
            </label>

            @if (form.invalid && form.touched) {
              <div class="form-warning full">
                Completá correctamente código, nombre,
                presentación, unidad, existencias y precio.
              </div>
            }

            <div class="actions full sticky-actions">
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
                    : 'Guardar medicamento'
                }}
              </button>
            </div>
          </form>
        </aside>
      </div>
    }

    @if (stockOpen() && selected()) {
      <div
        class="drawer-backdrop"
        (click)="closeStock()"
      >
        <aside
          class="drawer small"
          (click)="$event.stopPropagation()"
        >
          <div class="drawer-title">
            <div>
              <span class="eyebrow">Inventario</span>

              <h2>Actualizar stock</h2>

              <p>
                {{ selected()!.nombre }} ·
                actual {{ selected()!.stock_actual }}
              </p>
            </div>

            <button
              type="button"
              aria-label="Cerrar inventario"
              (click)="closeStock()"
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
            [formGroup]="stockForm"
            (ngSubmit)="saveStock()"
          >
            <label class="full">
              <span>Tipo *</span>

              <select formControlName="tipo">
                <option value="ENTRADA">
                  Entrada de unidades
                </option>

                <option value="AJUSTE">
                  Ajustar stock final
                </option>
              </select>
            </label>

            <label class="full">
              <span>Cantidad *</span>

              <input
                type="number"
                min="1"
                step="1"
                formControlName="cantidad"
              >
            </label>

            <label class="full">
              <span>Motivo *</span>

              <textarea
                rows="3"
                formControlName="motivo"
                placeholder="Ejemplo: Compra de medicamentos"
              ></textarea>
            </label>

            <div class="actions full sticky-actions">
              <button
                type="button"
                class="button secondary"
                (click)="closeStock()"
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
                    ? 'Registrando...'
                    : 'Registrar movimiento'
                }}
              </button>
            </div>
          </form>
        </aside>
      </div>
    }
  `,
  styles: [`
    .toolbar {
      align-items: center;
    }

    .check {
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--muted);
      font-size: 0.68rem;
      white-space: nowrap;
    }

    .check input {
      width: auto;
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
      font-size: 0.62rem;
      font-weight: 800;
      cursor: pointer;
    }

    .danger {
      color: #b42318;
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

    .form-warning {
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
      bottom: -24px;
      z-index: 5;
      margin: 10px -24px -24px;
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

    @media (max-width: 620px) {
      .toolbar {
        display: grid;
      }

      .sticky-actions {
        bottom: -20px;
        margin: 10px -16px -20px;
        padding: 14px 16px;
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MedicationsComponent {
  private readonly api = inject(ApiService);

  readonly items = signal<Medication[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly open = signal(false);
  readonly stockOpen = signal(false);
  readonly selected = signal<Medication | null>(null);
  readonly low = signal<boolean | null>(null);
  readonly error = signal('');
  readonly message = signal('');

  readonly form = new FormGroup({
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
        Validators.minLength(2),
        Validators.maxLength(150),
      ],
    }),

    presentacion: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(100),
      ],
    }),

    unidad: new FormControl('UNIDAD', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.maxLength(30),
      ],
    }),

    stock_actual: new FormControl(0, {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.min(0),
      ],
    }),

    stock_minimo: new FormControl(5, {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.min(0),
      ],
    }),

    precio_unitario: new FormControl(0, {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.min(0),
      ],
    }),
  });

  readonly stockForm = new FormGroup({
    tipo: new FormControl('ENTRADA', {
      nonNullable: true,
      validators: [Validators.required],
    }),

    cantidad: new FormControl(1, {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.min(1),
      ],
    }),

    motivo: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.minLength(3),
        Validators.maxLength(500),
      ],
    }),
  });

  constructor() {
    this.load();
  }

  load(search = ''): void {
    this.loading.set(true);
    this.error.set('');

    this.api.medications(
      search,
      this.low(),
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

  toggleLow(event: Event): void {
    const checked = (
      event.target as HTMLInputElement
    ).checked;

    this.low.set(checked ? true : null);
    this.load();
  }

  newMedication(): void {
    this.error.set('');
    this.message.set('');
    this.selected.set(null);

    this.form.reset({
      codigo: '',
      nombre: '',
      presentacion: '',
      unidad: 'UNIDAD',
      stock_actual: 0,
      stock_minimo: 5,
      precio_unitario: 0,
    });

    this.open.set(true);
  }

  edit(medication: Medication): void {
    this.error.set('');
    this.message.set('');
    this.selected.set(medication);

    this.form.reset({
      codigo: medication.codigo,
      nombre: medication.nombre,
      presentacion: medication.presentacion,
      unidad: medication.unidad,
      stock_actual: medication.stock_actual,
      stock_minimo: medication.stock_minimo,
      precio_unitario: Number(
        medication.precio_unitario,
      ),
    });

    this.open.set(true);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();

      this.error.set(
        'Completá correctamente todos los campos obligatorios.',
      );

      return;
    }

    if (this.saving()) {
      return;
    }

    this.saving.set(true);
    this.error.set('');

    const values = this.form.getRawValue();

    const commonPayload: MedicationPayload = {
      nombre: values.nombre.trim(),
      principio_activo: null,
      concentracion: null,
      presentacion: values.presentacion.trim(),
      unidad: values.unidad.trim().toUpperCase(),
      stock_minimo: Number(values.stock_minimo),
      precio_unitario: Number(
        values.precio_unitario,
      ),
    };

    const selectedMedication = this.selected();

    const request = selectedMedication
      ? this.api.updateMedication(
          selectedMedication.medicamento_id,
          commonPayload,
        )
      : this.api.createMedication({
          ...commonPayload,
          codigo: values.codigo
            .trim()
            .toUpperCase(),
          stock_actual: Number(
            values.stock_actual,
          ),
        });

    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.close();

        this.message.set(
          selectedMedication
            ? 'Medicamento actualizado correctamente.'
            : 'Medicamento registrado correctamente.',
        );

        this.load();
      },

      error: (error: unknown) => {
        this.saving.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  stock(medication: Medication): void {
    this.error.set('');
    this.message.set('');
    this.selected.set(medication);

    this.stockForm.reset({
      tipo: 'ENTRADA',
      cantidad: 1,
      motivo: '',
    });

    this.stockOpen.set(true);
  }

  saveStock(): void {
    if (this.stockForm.invalid) {
      this.stockForm.markAllAsTouched();

      this.error.set(
        'Completá la cantidad y el motivo del movimiento.',
      );

      return;
    }

    const medication = this.selected();

    if (!medication || this.saving()) {
      return;
    }

    this.saving.set(true);
    this.error.set('');

    const values = this.stockForm.getRawValue();

    this.api.stockMovement(
      medication.medicamento_id,
      values.tipo,
      Number(values.cantidad),
      values.motivo.trim(),
    ).subscribe({
      next: () => {
        this.saving.set(false);
        this.closeStock();

        this.message.set(
          'Movimiento de inventario registrado correctamente.',
        );

        this.load();
      },

      error: (error: unknown) => {
        this.saving.set(false);
        this.error.set(apiError(error));
      },
    });
  }

  close(): void {
    this.open.set(false);
    this.selected.set(null);
    this.error.set('');
  }

  closeStock(): void {
    this.stockOpen.set(false);
    this.selected.set(null);
    this.error.set('');
  }

  formatPrice(
    value: number | string | null | undefined,
  ): string {
    return Number(value ?? 0).toFixed(2);
  }
}