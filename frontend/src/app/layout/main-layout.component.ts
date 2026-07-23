import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../core/auth.service';
interface Nav {label:string;route:string;icon:string;group:string;}
@Component({selector:'app-main-layout',imports:[RouterOutlet,RouterLink,RouterLinkActive],template:`
<div class="shell">
 @if(menuOpen()){<button class="overlay" (click)="menuOpen.set(false)"></button>}
 <aside class="sidebar" [class.open]="menuOpen()">
  <a class="brand" routerLink="/dashboard"><span>H+</span><div><strong>Hospital Central</strong><small>Gestión Hospitalaria</small></div></a>
  <div class="nav-scroll">
   @for(group of groups;track group){<p class="group">{{group}}</p><nav>
    @for(item of itemsFor(group);track item.route){<a [routerLink]="item.route" routerLinkActive="active" (click)="menuOpen.set(false)"><b>{{item.icon}}</b>{{item.label}}</a>}
   </nav>}
  </div>
  <div class="api"><i></i><div><strong>Backend conectado</strong><small>FastAPI + Oracle</small></div></div>
 </aside>
 <div class="content">
  <header><button class="menu" (click)="menuOpen.update(v=>!v)">☰</button><div><small>Sistema de Gestión Hospitalaria</small><strong>Panel administrativo</strong></div><div class="user"><div><strong>{{auth.username()}}</strong><small>{{auth.roles().join(', ')}}</small></div><span>{{auth.username().slice(0,2).toUpperCase()}}</span><button (click)="auth.logout()">↪</button></div></header>
  <main><router-outlet/></main><footer><span>Hospital Central · Proyecto académico</span><span>Angular · FastAPI · Oracle</span></footer>
 </div>
</div>`,styles:[`
.sidebar{position:fixed;z-index:1000;inset:0 auto 0 0;width:270px;display:flex;flex-direction:column;padding:22px 14px;color:#d9e8fb;background:linear-gradient(180deg,#0e3a72,#08274f);transition:.2s}.brand{display:flex;align-items:center;gap:12px;padding:0 8px 20px;color:#fff;text-decoration:none}.brand>span{display:grid;width:44px;height:44px;place-items:center;border-radius:14px;color:#0e3a72;background:#fff;font-weight:900}.brand strong,.brand small{display:block}.brand strong{font-size:.9rem}.brand small{color:#a9c9ee;font-size:.65rem;margin-top:3px}.nav-scroll{overflow:auto;padding-right:3px}.group{margin:18px 12px 8px;color:#79a7d6;font-size:.61rem;font-weight:900;letter-spacing:.1em;text-transform:uppercase}nav{display:grid;gap:4px}nav a{display:flex;align-items:center;gap:11px;min-height:42px;padding:0 12px;border-radius:11px;color:#c9dcf5;text-decoration:none;font-size:.76rem;font-weight:700}nav a:hover{background:#ffffff12;color:#fff}nav a.active{color:#fff;background:linear-gradient(135deg,#38bdf83d,#2563eb4d);box-shadow:inset 3px 0 #7dd3fc}nav b{display:grid;width:25px;place-items:center}.api{display:flex;align-items:center;gap:10px;margin-top:auto;padding:13px;border:1px solid #ffffff18;border-radius:14px;background:#ffffff0e}.api i{width:10px;height:10px;border-radius:50%;background:#34d399;box-shadow:0 0 0 5px #34d39924}.api strong,.api small{display:block}.api strong{font-size:.68rem}.api small{color:#a8c8ef;font-size:.6rem;margin-top:3px}.content{min-height:100vh;margin-left:270px}header{position:sticky;z-index:100;top:0;display:flex;min-height:72px;align-items:center;justify-content:space-between;padding:10px 26px;border-bottom:1px solid var(--border);background:#f8fafce8;backdrop-filter:blur(14px)}header>div>small,header>div>strong{display:block}header>div>small{color:var(--muted);font-size:.64rem}header>div>strong{font-size:.9rem;margin-top:3px}.user{display:flex;align-items:center;gap:9px}.user>div{text-align:right}.user span{display:grid;width:38px;height:38px;place-items:center;border-radius:12px;color:#fff;background:linear-gradient(135deg,#155eef,#38bdf8);font-size:.68rem;font-weight:900}.user button,.menu{display:grid;width:38px;height:38px;place-items:center;border:1px solid var(--border);border-radius:11px;background:#fff;color:var(--muted);cursor:pointer}.menu{display:none}main{width:min(100%,1550px);min-height:calc(100vh - 125px);margin:auto;padding:25px 27px}footer{display:flex;justify-content:space-between;padding:8px 27px 22px;color:#98a2b3;font-size:.64rem}.overlay{display:none}@media(max-width:1000px){.sidebar{transform:translateX(-105%)}.sidebar.open{transform:none}.content{margin-left:0}.menu{display:grid}.overlay{position:fixed;z-index:999;inset:0;display:block;border:0;background:#0f172a7a}}@media(max-width:620px){main{padding:20px 14px}header{padding-inline:14px}.user>div{display:none}footer{display:grid;gap:5px;padding-inline:14px}}
`],changeDetection:ChangeDetectionStrategy.OnPush})
export class MainLayoutComponent{
 readonly menuOpen=signal(false);readonly groups=['Principal','Clínica y farmacia','Administración'];
 readonly nav:Nav[]=[
 {label:'Dashboard',route:'/dashboard',icon:'⌂',group:'Principal'},{label:'Pacientes',route:'/pacientes',icon:'P',group:'Principal'},{label:'Médicos',route:'/medicos',icon:'M',group:'Principal'},{label:'Citas médicas',route:'/citas',icon:'C',group:'Principal'},{label:'Consultas clínicas',route:'/consultas',icon:'+',group:'Principal'},
 {label:'Medicamentos',route:'/medicamentos',icon:'Rx',group:'Clínica y farmacia'},{label:'Recetas',route:'/recetas',icon:'R',group:'Clínica y farmacia'},{label:'Laboratorio',route:'/laboratorio',icon:'L',group:'Clínica y farmacia'},{label:'Habitaciones',route:'/habitaciones',icon:'H',group:'Clínica y farmacia'},
 {label:'Facturación',route:'/facturacion',icon:'Q',group:'Administración'},{label:'Especialidades',route:'/especialidades',icon:'E',group:'Administración'},{label:'Usuarios',route:'/usuarios',icon:'U',group:'Administración'},{label:'Auditoría',route:'/auditoria',icon:'A',group:'Administración'},{label:'Reportes',route:'/reportes',icon:'▥',group:'Administración'}];
 constructor(readonly auth:AuthService){} itemsFor(g:string){return this.nav.filter(x=>x.group===g);}
}
