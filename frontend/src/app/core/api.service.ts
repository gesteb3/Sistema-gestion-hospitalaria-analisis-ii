import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import * as M from './models';

@Injectable({providedIn:'root'})
export class ApiService {
  private readonly http=inject(HttpClient);
  private readonly base=environment.apiUrl;
  private params(extra:Record<string,string|number|boolean|undefined|null>={}):HttpParams{
    let p=new HttpParams();
    for(const [key,value] of Object.entries(extra)){if(value!==undefined&&value!==null&&value!=='')p=p.set(key,String(value));}
    return p;
  }
  dashboard():Observable<M.DashboardReport>{return this.http.get<M.DashboardReport>(`${this.base}/reports/dashboard`);}
  clinicalReport():Observable<M.ClinicalReport>{return this.http.get<M.ClinicalReport>(`${this.base}/reports/clinical`);}
  financialReport():Observable<M.FinancialReport>{return this.http.get<M.FinancialReport>(`${this.base}/reports/financial`);}
  systemReport():Observable<M.SystemReport>{return this.http.get<M.SystemReport>(`${this.base}/reports/system`);}

  patients(search='',includeInactive=true):Observable<M.Paginated<M.Patient>>{return this.http.get<M.Paginated<M.Patient>>(`${this.base}/patients`,{params:this.params({search,page:1,page_size:100,include_inactive:includeInactive})});}
  createPatient(body:M.PatientPayload):Observable<M.Patient>{return this.http.post<M.Patient>(`${this.base}/patients`,body);}
  updatePatient(id:number,body:M.PatientPayload):Observable<M.Patient>{return this.http.put<M.Patient>(`${this.base}/patients/${id}`,body);}
  deactivatePatient(id:number):Observable<M.MessageResponse>{return this.http.delete<M.MessageResponse>(`${this.base}/patients/${id}`);}
  reactivatePatient(id:number):Observable<M.Patient>{return this.http.patch<M.Patient>(`${this.base}/patients/${id}/reactivate`,{});}

  specialties(includeInactive=true):Observable<M.Specialty[]>{return this.http.get<M.Specialty[]>(`${this.base}/specialties`,{params:this.params({include_inactive:includeInactive})});}
  createSpecialty(body:M.SpecialtyPayload):Observable<M.Specialty>{return this.http.post<M.Specialty>(`${this.base}/specialties`,body);}
  updateSpecialty(id:number,body:M.SpecialtyPayload):Observable<M.Specialty>{return this.http.put<M.Specialty>(`${this.base}/specialties/${id}`,body);}
  deactivateSpecialty(id:number):Observable<M.MessageResponse>{return this.http.delete<M.MessageResponse>(`${this.base}/specialties/${id}`);}
  reactivateSpecialty(id:number):Observable<M.Specialty>{return this.http.patch<M.Specialty>(`${this.base}/specialties/${id}/reactivate`,{});}

  doctors(search='',includeInactive=true):Observable<M.Paginated<M.Doctor>>{return this.http.get<M.Paginated<M.Doctor>>(`${this.base}/doctors`,{params:this.params({search,page:1,page_size:100,include_inactive:includeInactive})});}
  createDoctor(body:M.DoctorPayload):Observable<M.Doctor>{return this.http.post<M.Doctor>(`${this.base}/doctors`,body);}
  updateDoctor(id:number,body:M.DoctorPayload):Observable<M.Doctor>{return this.http.put<M.Doctor>(`${this.base}/doctors/${id}`,body);}
  deactivateDoctor(id:number):Observable<M.MessageResponse>{return this.http.delete<M.MessageResponse>(`${this.base}/doctors/${id}`);}
  reactivateDoctor(id:number):Observable<M.Doctor>{return this.http.patch<M.Doctor>(`${this.base}/doctors/${id}/reactivate`,{});}
  createSchedule(doctorId:number,body:M.SchedulePayload):Observable<M.DoctorSchedule>{return this.http.post<M.DoctorSchedule>(`${this.base}/doctors/${doctorId}/schedules`,body);}
  deleteSchedule(doctorId:number,scheduleId:number):Observable<M.MessageResponse>{return this.http.delete<M.MessageResponse>(`${this.base}/doctors/${doctorId}/schedules/${scheduleId}`);}

  appointments(status=''):Observable<M.Paginated<M.Appointment>>{return this.http.get<M.Paginated<M.Appointment>>(`${this.base}/appointments`,{params:this.params({status,page:1,page_size:100})});}
  createAppointment(body:M.AppointmentCreate):Observable<M.Appointment>{return this.http.post<M.Appointment>(`${this.base}/appointments`,body);}
  updateAppointment(id:number,body:M.AppointmentUpdate):Observable<M.Appointment>{return this.http.put<M.Appointment>(`${this.base}/appointments/${id}`,body);}
  updateAppointmentStatus(id:number,estado:string,motivo_cancelacion:string|null=null):Observable<M.Appointment>{return this.http.patch<M.Appointment>(`${this.base}/appointments/${id}/status`,{estado,motivo_cancelacion});}
  availability(doctorId:number,date:string):Observable<M.Availability>{return this.http.get<M.Availability>(`${this.base}/appointments/availability`,{params:this.params({doctor_id:doctorId,date})});}

  consultations():Observable<M.Paginated<M.Consultation>>{return this.http.get<M.Paginated<M.Consultation>>(`${this.base}/consultations`,{params:this.params({page:1,page_size:100})});}
  createConsultation(body:M.ConsultationCreate):Observable<M.Consultation>{return this.http.post<M.Consultation>(`${this.base}/consultations`,body);}

  users():Observable<M.User[]>{return this.http.get<M.User[]>(`${this.base}/users`);}
  createUser(body:M.UserCreate):Observable<M.User>{return this.http.post<M.User>(`${this.base}/users`,body);}

  medications(search='',lowStock:boolean|null=null):Observable<M.Paginated<M.Medication>>{return this.http.get<M.Paginated<M.Medication>>(`${this.base}/medications`,{params:this.params({search,low_stock:lowStock,page:1,page_size:100,include_inactive:true})});}
  createMedication(body:M.MedicationPayload):Observable<M.Medication>{return this.http.post<M.Medication>(`${this.base}/medications`,body);}
  updateMedication(id:number,body:M.MedicationPayload):Observable<M.Medication>{return this.http.put<M.Medication>(`${this.base}/medications/${id}`,body);}
  stockMovement(id:number,tipo:string,cantidad:number,motivo:string):Observable<M.InventoryMovement>{return this.http.post<M.InventoryMovement>(`${this.base}/medications/${id}/stock`,{tipo,cantidad,motivo});}

  prescriptions(status=''):Observable<M.Paginated<M.Prescription>>{return this.http.get<M.Paginated<M.Prescription>>(`${this.base}/prescriptions`,{params:this.params({status,page:1,page_size:100})});}
  createPrescription(body:M.PrescriptionCreate):Observable<M.Prescription>{return this.http.post<M.Prescription>(`${this.base}/prescriptions`,body);}
  dispensePrescription(id:number):Observable<M.Prescription>{return this.http.patch<M.Prescription>(`${this.base}/prescriptions/${id}/dispense`,{});}
  cancelPrescription(id:number,reason:string):Observable<M.Prescription>{return this.http.patch<M.Prescription>(`${this.base}/prescriptions/${id}/cancel`,{motivo_anulacion:reason});}

  labTests():Observable<M.LabTestType[]>{return this.http.get<M.LabTestType[]>(`${this.base}/lab-tests`,{params:this.params({include_inactive:true})});}
  createLabTest(body:M.LabTestPayload):Observable<M.LabTestType>{return this.http.post<M.LabTestType>(`${this.base}/lab-tests`,body);}
  updateLabTest(id:number,body:M.LabTestPayload):Observable<M.LabTestType>{return this.http.put<M.LabTestType>(`${this.base}/lab-tests/${id}`,body);}
  labOrders(status=''):Observable<M.Paginated<M.LabOrder>>{return this.http.get<M.Paginated<M.LabOrder>>(`${this.base}/lab-orders`,{params:this.params({status,page:1,page_size:100})});}
  createLabOrder(body:M.LabOrderCreate):Observable<M.LabOrder>{return this.http.post<M.LabOrder>(`${this.base}/lab-orders`,body);}
  updateLabOrderStatus(id:number,estado:string,motivo_cancelacion:string|null=null):Observable<M.LabOrder>{return this.http.patch<M.LabOrder>(`${this.base}/lab-orders/${id}/status`,{estado,motivo_cancelacion});}
  saveLabResult(orderId:number,itemId:number,body:{resultado:string;valores_referencia:string|null;interpretacion:string|null;archivo_url:string|null;}):Observable<M.LabOrder>{return this.http.post<M.LabOrder>(`${this.base}/lab-orders/${orderId}/items/${itemId}/result`,body);}

  billingSummary():Observable<M.BillingSummary>{return this.http.get<M.BillingSummary>(`${this.base}/billing/summary`);}
  invoices(status=''):Observable<M.Paginated<M.Invoice>>{return this.http.get<M.Paginated<M.Invoice>>(`${this.base}/billing/invoices`,{params:this.params({status,page:1,page_size:100})});}
  createInvoice(body:M.InvoiceCreate):Observable<M.Invoice>{return this.http.post<M.Invoice>(`${this.base}/billing/invoices`,body);}
  payInvoice(id:number,monto:number,metodo_pago:string,referencia:string|null,observaciones:string|null):Observable<M.Invoice>{return this.http.post<M.Invoice>(`${this.base}/billing/invoices/${id}/payments`,{monto,metodo_pago,referencia,observaciones});}
  cancelInvoice(id:number,reason:string):Observable<M.Invoice>{return this.http.patch<M.Invoice>(`${this.base}/billing/invoices/${id}/cancel`,{motivo_anulacion:reason});}

  auditLogs(module='',successful:string=''):Observable<M.Paginated<M.AuditLog>>{return this.http.get<M.Paginated<M.AuditLog>>(`${this.base}/audit-logs`,{params:this.params({module,successful:successful===''?undefined:successful,page:1,page_size:100})});}
}
