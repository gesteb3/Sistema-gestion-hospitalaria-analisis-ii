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
import { Router } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  template: `
    <div class="login-page">
      <section class="visual">
        <div>
          <span class="tag">Plataforma hospitalaria</span>
          <h1>
            Atención organizada,
            <em>información segura.</em>
          </h1>
          <p>
            Administra pacientes, médicos y citas desde
            una interfaz limpia, moderna y profesional.
          </p>

          <div class="features">
            <article>
              <strong>01</strong>
              <span>Gestión clínica centralizada</span>
            </article>
            <article>
              <strong>02</strong>
              <span>Acceso protegido por roles</span>
            </article>
            <article>
              <strong>03</strong>
              <span>Indicadores operativos</span>
            </article>
          </div>
        </div>
      </section>

      <section class="form-side">
        <form [formGroup]="form" (ngSubmit)="submit()">
          <div class="brand">
            <span>H+</span>
            <div>
              <strong>Hospital Central</strong>
              <small>Sistema de Gestión Hospitalaria</small>
            </div>
          </div>

          <span class="eyebrow">Bienvenido</span>
          <h2>Iniciar sesión</h2>
          <p class="intro">
            Ingresá tus credenciales para acceder al sistema.
          </p>

          @if (error()) {
            <div class="alert">{{ error() }}</div>
          }

          <label>
            <span>Usuario</span>
            <input
              type="text"
              formControlName="username"
              autocomplete="username"
            >
          </label>

          <label>
            <span>Contraseña</span>
            <input
              type="password"
              formControlName="password"
              autocomplete="current-password"
            >
          </label>

          <button
            class="primary"
            type="submit"
            [disabled]="loading()"
          >
            {{ loading() ? 'Ingresando...' : 'Ingresar al sistema →' }}
          </button>

          <div class="credentials">
            <strong>Acceso inicial</strong>
            <span>admin / Admin12345</span>
          </div>
        </form>
      </section>
    </div>
  `,
  styles: [`
    .login-page {
      display: grid;
      min-height: 100vh;
      grid-template-columns: minmax(0, 1.15fr) minmax(420px, .85fr);
      background: #f8fafc;
    }

    .visual {
      display: flex;
      align-items: center;
      overflow: hidden;
      padding: clamp(40px, 8vw, 100px);
      color: #fff;
      background:
        radial-gradient(circle at 80% 20%, rgb(56 189 248 / 35%), transparent 28%),
        radial-gradient(circle at 15% 85%, rgb(37 99 235 / 45%), transparent 32%),
        linear-gradient(145deg, #0b2d5c, #155eef);
    }

    .visual > div {
      max-width: 680px;
    }

    .tag {
      display: inline-flex;
      padding: 7px 12px;
      border: 1px solid rgb(255 255 255 / 18%);
      border-radius: 999px;
      color: #c9ebff;
      background: rgb(255 255 255 / 8%);
      font-size: .68rem;
      font-weight: 800;
      text-transform: uppercase;
    }

    h1 {
      margin: 25px 0 20px;
      font-size: clamp(2.8rem, 6vw, 5.2rem);
      line-height: .98;
      letter-spacing: -.055em;
    }

    h1 em {
      display: block;
      color: #7dd3fc;
      font-style: normal;
    }

    .visual p {
      max-width: 560px;
      color: #d5e8ff;
      line-height: 1.75;
    }

    .features {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-top: 45px;
    }

    .features article {
      display: grid;
      gap: 8px;
      padding: 16px;
      border: 1px solid rgb(255 255 255 / 12%);
      border-radius: 16px;
      background: rgb(255 255 255 / 7%);
    }

    .features strong {
      color: #7dd3fc;
      font-size: .68rem;
    }

    .features span {
      font-size: .75rem;
      font-weight: 700;
      line-height: 1.5;
    }

    .form-side {
      display: grid;
      place-items: center;
      padding: 38px;
    }

    form {
      display: grid;
      width: min(100%, 440px);
      gap: 18px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 25px;
    }

    .brand > span {
      display: grid;
      width: 46px;
      height: 46px;
      place-items: center;
      border-radius: 14px;
      color: #fff;
      background: linear-gradient(135deg, #155eef, #38bdf8);
      font-weight: 900;
    }

    .brand strong,
    .brand small {
      display: block;
    }

    .brand strong {
      font-size: .86rem;
    }

    .brand small {
      margin-top: 3px;
      color: var(--muted);
      font-size: .66rem;
    }

    .eyebrow {
      color: var(--primary);
      font-size: .72rem;
      font-weight: 900;
      text-transform: uppercase;
    }

    h2 {
      margin: -10px 0 -8px;
      color: var(--text);
      font-size: 2rem;
    }

    .intro {
      margin: 0 0 5px;
      color: var(--muted);
      line-height: 1.6;
    }

    label {
      display: grid;
      gap: 7px;
    }

    label span {
      color: var(--text);
      font-size: .72rem;
      font-weight: 800;
    }

    input {
      min-height: 45px;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 11px;
      outline: 0;
      background: #fff;
    }

    input:focus {
      border-color: #84adff;
      box-shadow: 0 0 0 3px rgb(21 94 239 / 9%);
    }

    .primary {
      min-height: 48px;
      border: 0;
      border-radius: 11px;
      color: #fff;
      background: var(--primary);
      font-weight: 800;
      cursor: pointer;
    }

    .primary:disabled {
      opacity: .6;
    }

    .alert {
      padding: 12px 14px;
      border: 1px solid #fecdca;
      border-radius: 11px;
      color: #b42318;
      background: #fef3f2;
      font-size: .75rem;
    }

    .credentials {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 13px 15px;
      border: 1px dashed #b9d7ff;
      border-radius: 11px;
      color: #175cd3;
      background: #f0f7ff;
      font-size: .72rem;
    }

    @media (max-width: 950px) {
      .login-page {
        grid-template-columns: 1fr;
      }

      .visual {
        min-height: 330px;
        padding: 48px 28px;
      }
    }

    @media (max-width: 580px) {
      .features {
        grid-template-columns: 1fr;
      }

      .form-side {
        padding: 40px 20px;
      }

      .credentials {
        display: grid;
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly loading = signal(false);
  readonly error = signal('');

  readonly form = new FormGroup({
    username: new FormControl('admin', {
      nonNullable: true,
      validators: [Validators.required],
    }),
    password: new FormControl('Admin12345', {
      nonNullable: true,
      validators: [Validators.required],
    }),
  });

  submit(): void {
    if (this.form.invalid || this.loading()) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.error.set('');

    const value = this.form.getRawValue();

    this.auth.login(value.username, value.password).subscribe({
      next: () => {
        this.loading.set(false);
        void this.router.navigate(['/dashboard']);
      },
      error: () => {
        this.loading.set(false);
        this.error.set(
          'No fue posible iniciar sesión. Verificá las credenciales y el backend.',
        );
      },
    });
  }
}
