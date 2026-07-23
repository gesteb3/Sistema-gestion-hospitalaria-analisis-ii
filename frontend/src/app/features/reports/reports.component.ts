import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';
import { forkJoin } from 'rxjs';

import {
  ClinicalReport,
  FinancialReport,
  SystemReport,
} from '../../core/models';
import { ApiService } from '../../core/api.service';

@Component({
  selector: 'app-reports',
  imports: [CommonModule],
  template: `
    <section class="page-header">
      <div>
        <span class="eyebrow">Analítica hospitalaria</span>
        <h1>Reportes</h1>
        <p>Resumen clínico, financiero y operativo.</p>
      </div>
    </section>

    @if (loading()) {
      <div class="loading">Preparando reportes...</div>
    } @else {
      @if (financial(); as finance) {
        <section class="stats">
          <article>
            <small>Total facturado</small>
            <strong>
              {{ finance.total_facturado | currency:'GTQ':'symbol-narrow' }}
            </strong>
          </article>
          <article>
            <small>Total pagado</small>
            <strong>
              {{ finance.total_pagado | currency:'GTQ':'symbol-narrow' }}
            </strong>
          </article>
          <article>
            <small>Saldo pendiente</small>
            <strong>
              {{ finance.saldo_pendiente | currency:'GTQ':'symbol-narrow' }}
            </strong>
          </article>
          <article>
            <small>Pagos registrados</small>
            <strong>{{ finance.cantidad_pagos }}</strong>
          </article>
        </section>
      }

      <section class="report-grid">
        @if (clinical(); as clinicalData) {
          <article class="panel report">
            <span class="eyebrow">Actividad clínica</span>
            <h2>Citas por estado</h2>
            @for (
              item of clinicalData.citas_por_estado;
              track item.estado
            ) {
              <div class="report-row">
                <span
                  class="badge"
                  [attr.data-status]="item.estado"
                >
                  {{ item.estado.replaceAll('_', ' ') }}
                </span>
                <strong>{{ item.cantidad }}</strong>
              </div>
            }
          </article>

          <article class="panel report">
            <span class="eyebrow">Laboratorio</span>
            <h2>Órdenes por estado</h2>
            @for (
              item of clinicalData.ordenes_laboratorio_por_estado;
              track item.estado
            ) {
              <div class="report-row">
                <span
                  class="badge"
                  [attr.data-status]="item.estado"
                >
                  {{ item.estado.replaceAll('_', ' ') }}
                </span>
                <strong>{{ item.cantidad }}</strong>
              </div>
            }
          </article>
        }

        @if (system(); as systemData) {
          <article class="panel report">
            <span class="eyebrow">Sistema</span>
            <h2>Auditoría</h2>
            <div class="report-row">
              <span>Usuarios activos</span>
              <strong>{{ systemData.usuarios_activos }}</strong>
            </div>
            <div class="report-row">
              <span>Eventos auditados</span>
              <strong>{{ systemData.eventos_auditoria }}</strong>
            </div>
            <div class="report-row">
              <span>Eventos exitosos</span>
              <strong>{{ systemData.eventos_exitosos }}</strong>
            </div>
            <div class="report-row">
              <span>Eventos fallidos</span>
              <strong>{{ systemData.eventos_fallidos }}</strong>
            </div>
          </article>
        }
      </section>
    }
  `,
  styles: [`
    .stats {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-top: 22px;
    }

    .stats article {
      padding: 20px;
      border: 1px solid var(--border);
      border-radius: 18px;
      background: #fff;
      box-shadow: var(--shadow);
    }

    .stats small,
    .stats strong {
      display: block;
    }

    .stats small {
      color: var(--muted);
      font-size: .7rem;
      font-weight: 800;
    }

    .stats strong {
      margin-top: 10px;
      font-size: 1.35rem;
    }

    .report-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-top: 20px;
    }

    .report {
      padding: 20px;
    }

    .report h2 {
      margin: 5px 0 20px;
      font-size: .95rem;
    }

    .report-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 15px;
      padding: 11px 0;
      border-bottom: 1px solid var(--border);
      color: var(--muted);
      font-size: .72rem;
    }

    .report-row:last-child {
      border-bottom: 0;
    }

    .report-row strong {
      color: var(--text);
    }

    @media (max-width: 1050px) {
      .stats,
      .report-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 650px) {
      .stats,
      .report-grid {
        grid-template-columns: 1fr;
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReportsComponent {
  private readonly api = inject(ApiService);

  readonly loading = signal(true);
  readonly clinical = signal<ClinicalReport | null>(null);
  readonly financial = signal<FinancialReport | null>(null);
  readonly system = signal<SystemReport | null>(null);

  constructor() {
    forkJoin({
      clinical: this.api.clinicalReport(),
      financial: this.api.financialReport(),
      system: this.api.systemReport(),
    }).subscribe({
      next: value => {
        this.clinical.set(value.clinical);
        this.financial.set(value.financial);
        this.system.set(value.system);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }
}
