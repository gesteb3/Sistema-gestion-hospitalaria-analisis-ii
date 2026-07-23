import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-placeholder',
  template: `
    <section class="page-header">
      <div>
        <span class="eyebrow">Módulo hospitalario</span>
        <h1>{{ title }}</h1>
        <p>{{ description }}</p>
      </div>
    </section>

    <section class="panel placeholder">
      <span>+</span>
      <h2>Módulo pendiente en el backend</h2>
      <p>
        La navegación y la pantalla ya están preparadas.
        No se muestran datos simulados porque todavía no existe
        un endpoint funcional para esta sección.
      </p>
    </section>
  `,
  styles: [`
    .placeholder {
      display: grid;
      min-height: 330px;
      place-items: center;
      align-content: center;
      gap: 9px;
      margin-top: 22px;
      padding: 30px;
      text-align: center;
    }

    .placeholder > span {
      display: grid;
      width: 58px;
      height: 58px;
      place-items: center;
      border-radius: 18px;
      color: var(--primary);
      background: #eaf2ff;
      font-size: 1.7rem;
    }

    h2,
    p {
      margin: 0;
    }

    h2 {
      margin-top: 10px;
      font-size: 1rem;
    }

    p {
      max-width: 520px;
      color: var(--muted);
      font-size: .76rem;
      line-height: 1.7;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlaceholderComponent {
  private readonly route = inject(ActivatedRoute);

  readonly title =
    this.route.snapshot.data['title'] as string;
  readonly description =
    this.route.snapshot.data['description'] as string;
}
