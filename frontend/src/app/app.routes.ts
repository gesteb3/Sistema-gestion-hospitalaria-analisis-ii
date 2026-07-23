import { Routes } from '@angular/router';
import { authGuard } from './core/auth.guard';
export const routes:Routes=[
 {path:'login',loadComponent:()=>import('./features/login/login.component').then(m=>m.LoginComponent)},
 {path:'',canActivate:[authGuard],loadComponent:()=>import('./layout/main-layout.component').then(m=>m.MainLayoutComponent),children:[
  {path:'dashboard',loadComponent:()=>import('./features/dashboard/dashboard.component').then(m=>m.DashboardComponent)},
  {path:'pacientes',loadComponent:()=>import('./features/patients/patients.component').then(m=>m.PatientsComponent)},
  {path:'medicos',loadComponent:()=>import('./features/doctors/doctors.component').then(m=>m.DoctorsComponent)},
  {path:'citas',loadComponent:()=>import('./features/appointments/appointments.component').then(m=>m.AppointmentsComponent)},
  {path:'consultas',loadComponent:()=>import('./features/consultations/consultations.component').then(m=>m.ConsultationsComponent)},
  {path:'medicamentos',loadComponent:()=>import('./features/medications/medications.component').then(m=>m.MedicationsComponent)},
  {path:'recetas',loadComponent:()=>import('./features/prescriptions/prescriptions.component').then(m=>m.PrescriptionsComponent)},
  {path:'laboratorio',loadComponent:()=>import('./features/laboratory/laboratory.component').then(m=>m.LaboratoryComponent)},
  {path:'facturacion',loadComponent:()=>import('./features/billing/billing.component').then(m=>m.BillingComponent)},
  {path:'especialidades',loadComponent:()=>import('./features/specialties/specialties.component').then(m=>m.SpecialtiesComponent)},
  {path:'usuarios',loadComponent:()=>import('./features/users/users.component').then(m=>m.UsersComponent)},
  {path:'auditoria',loadComponent:()=>import('./features/audit/audit.component').then(m=>m.AuditComponent)},
  {path:'reportes',loadComponent:()=>import('./features/reports/reports.component').then(m=>m.ReportsComponent)},
  {path:'habitaciones',loadComponent:()=>import('./features/placeholder/placeholder.component').then(m=>m.PlaceholderComponent),data:{title:'Habitaciones',description:'El backend todavía no posee endpoints para habitaciones; no se muestran datos simulados.'}},
  {path:'',pathMatch:'full',redirectTo:'dashboard'}
 ]},
 {path:'**',redirectTo:''}
];
