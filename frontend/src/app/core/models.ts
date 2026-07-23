export interface Paginated<T> { items:T[]; total:number; page:number; page_size:number; total_pages:number; }
export interface MessageResponse { message:string; }
export interface AuthSession { access_token:string; token_type:string; expires_in_minutes:number; usuario:string; roles:string[]; }

export interface User { usuario_id:number; nombre_usuario:string; correo:string; nombres:string; apellidos:string; activo:boolean; roles:string[]; fecha_creacion:string; ultimo_acceso:string|null; }
export interface UserCreate { nombre_usuario:string; password:string; correo:string; nombres:string; apellidos:string; roles:string[]; }

export interface DashboardReport { pacientes_activos:number; medicos_activos:number; citas_totales:number; citas_programadas:number; consultas_realizadas:number; ordenes_laboratorio_pendientes:number; recetas_emitidas:number; medicamentos_stock_bajo:number; facturas_pendientes:number; total_facturado:number; total_pagado:number; saldo_pendiente:number; }
export interface StatusCount { estado:string; cantidad:number; }
export interface ClinicalReport { pacientes_activos:number; consultas_realizadas:number; citas_por_estado:StatusCount[]; ordenes_laboratorio_por_estado:StatusCount[]; recetas_por_estado:StatusCount[]; }
export interface FinancialReport { total_facturado:number; total_pagado:number; saldo_pendiente:number; facturas_por_estado:StatusCount[]; cantidad_pagos:number; monto_promedio_factura:number; }
export interface SystemReport { usuarios_activos:number; medicos_activos:number; pacientes_activos:number; eventos_auditoria:number; eventos_exitosos:number; eventos_fallidos:number; }

export interface LegalGuardian { responsable_id?:number; nombres:string; apellidos:string; identificacion:string; parentesco:string; telefono:string; correo:string|null; principal?:boolean; }
export interface Patient { paciente_id:number; numero_expediente:string; nombres:string; apellidos:string; fecha_nacimiento:string; edad:number; menor_de_edad:boolean; sexo:string; identificacion:string|null; telefono:string|null; correo:string|null; direccion:string|null; activo:boolean; responsables_legales:LegalGuardian[]; fecha_creacion:string; fecha_actualizacion:string; }
export interface PatientPayload { nombres:string; apellidos:string; fecha_nacimiento:string; sexo:string; identificacion:string|null; telefono:string|null; correo:string|null; direccion:string|null; responsable_legal:LegalGuardian|null; }

export interface Specialty { especialidad_id:number; nombre:string; descripcion:string|null; activa:boolean; fecha_creacion:string; }
export interface SpecialtyPayload { nombre:string; descripcion:string|null; }

export interface DoctorSchedule { horario_id:number; dia_semana:number; nombre_dia:string; hora_inicio:string; hora_fin:string; duracion_cita_minutos:number; activo:boolean; }
export interface Doctor { medico_id:number; nombres:string; apellidos:string; nombre_completo:string; numero_colegiado:string; telefono:string|null; correo:string; direccion:string|null; activo:boolean; especialidades:Specialty[]; horarios:DoctorSchedule[]; fecha_creacion:string; fecha_actualizacion:string; }
export interface DoctorPayload { nombres:string; apellidos:string; numero_colegiado:string; telefono:string|null; correo:string; direccion:string|null; especialidad_ids:number[]; }
export interface SchedulePayload { dia_semana:number; hora_inicio:string; hora_fin:string; duracion_cita_minutos:number; }

export interface Appointment { cita_id:number; paciente_id:number; numero_expediente:string; paciente_nombre:string; medico_id:number; medico_nombre:string; numero_colegiado:string; especialidades:string[]; fecha:string; hora:string; hora_fin:string; duracion_minutos:number; motivo:string; observaciones:string|null; estado:string; motivo_cancelacion:string|null; fecha_creacion:string; fecha_actualizacion:string; }
export interface AppointmentCreate { paciente_id:number; medico_id:number; fecha:string; hora:string; motivo:string; observaciones:string|null; }
export interface AppointmentUpdate { medico_id?:number; fecha?:string; hora?:string; motivo?:string; observaciones?:string|null; }
export interface Availability { medico_id:number; medico_nombre:string; fecha:string; nombre_dia:string; horarios_configurados:boolean; espacios_disponibles:{ hora:string; hora_fin:string; duracion_minutos:number; }[]; }

export interface VitalSigns { signo_vital_id:number; temperatura_c:number|null; presion_sistolica:number|null; presion_diastolica:number|null; presion_arterial:string|null; frecuencia_cardiaca:number|null; frecuencia_respiratoria:number|null; saturacion_oxigeno:number|null; peso_kg:number|null; estatura_cm:number|null; imc:number|null; observaciones:string|null; fecha_registro:string; }
export interface Diagnosis { diagnostico_id:number; codigo_cie10:string|null; descripcion:string; tipo:string; principal:boolean; fecha_registro:string; }
export interface Treatment { tratamiento_id:number; descripcion:string; duracion:string|null; indicaciones:string|null; estado:string; fecha_registro:string; }
export interface Consultation { consulta_id:number; historial_id:number; cita_id:number; paciente_id:number; numero_expediente:string; paciente_nombre:string; medico_id:number; medico_nombre:string; fecha_atencion:string; motivo_consulta:string; sintomas:string|null; evaluacion_clinica:string; indicaciones_generales:string|null; notas_medicas:string|null; signos_vitales:VitalSigns|null; diagnosticos:Diagnosis[]; tratamientos:Treatment[]; fecha_actualizacion:string; }
export interface ConsultationCreate { cita_id:number; medico_id:number; motivo_consulta:string; sintomas:string|null; evaluacion_clinica:string; indicaciones_generales:string|null; notas_medicas:string|null; signos_vitales:null|{temperatura_c:number|null;presion_sistolica:number|null;presion_diastolica:number|null;frecuencia_cardiaca:number|null;frecuencia_respiratoria:number|null;saturacion_oxigeno:number|null;peso_kg:number|null;estatura_cm:number|null;observaciones:string|null}; diagnosticos:{codigo_cie10:string|null;descripcion:string;tipo:string;es_principal:boolean;}[]; tratamientos:{descripcion:string;duracion:string|null;indicaciones:string|null;estado:string;}[]; }

export interface Medication { medicamento_id:number; codigo:string; nombre:string; principio_activo:string|null; concentracion:string|null; presentacion:string; unidad:string; stock_actual:number; stock_minimo:number; stock_bajo:boolean; precio_unitario:number; activo:boolean; fecha_creacion:string; fecha_actualizacion:string; }
export interface MedicationPayload { codigo?:string; nombre:string; principio_activo:string|null; concentracion:string|null; presentacion:string; unidad:string; stock_actual?:number; stock_minimo:number; precio_unitario:number; }
export interface InventoryMovement { movimiento_id:number; medicamento_id:number; medicamento_nombre:string; receta_id:number|null; tipo:string; cantidad:number; stock_anterior:number; stock_nuevo:number; motivo:string; fecha_movimiento:string; }

export interface PrescriptionItem { detalle_receta_id:number; medicamento_id:number; medicamento_codigo:string; medicamento_nombre:string; dosis:string; via_administracion:string; frecuencia:string; duracion:string; cantidad:number; cantidad_dispensada:number; indicaciones:string|null; }
export interface Prescription { receta_id:number; consulta_id:number; paciente_id:number; numero_expediente:string; paciente_nombre:string; medico_id:number; medico_nombre:string; indicaciones_generales:string|null; estado:string; motivo_anulacion:string|null; items:PrescriptionItem[]; fecha_emision:string; fecha_dispensacion:string|null; }
export interface PrescriptionCreate { consulta_id:number; indicaciones_generales:string|null; items:{medicamento_id:number;dosis:string;via_administracion:string;frecuencia:string;duracion:string;cantidad:number;indicaciones:string|null;}[]; }

export interface LabTestType { tipo_examen_id:number; codigo:string; nombre:string; descripcion:string|null; muestra_requerida:string; tiempo_estimado_horas:number; precio:number; activo:boolean; fecha_creacion:string; }
export interface LabTestPayload { codigo?:string; nombre:string; descripcion:string|null; muestra_requerida:string; tiempo_estimado_horas:number; precio:number; }
export interface LabResult { resultado_id:number; resultado:string; valores_referencia:string|null; interpretacion:string|null; archivo_url:string|null; fecha_resultado:string; }
export interface LabOrderItem { detalle_orden_id:number; tipo_examen_id:number; codigo_examen:string; nombre_examen:string; muestra_requerida:string; precio:number; observaciones:string|null; estado:string; fecha_procesamiento:string|null; resultado:LabResult|null; }
export interface LabOrder { orden_laboratorio_id:number; consulta_id:number; paciente_id:number; numero_expediente:string; paciente_nombre:string; medico_id:number; medico_nombre:string; indicaciones:string|null; prioridad:string; estado:string; motivo_cancelacion:string|null; items:LabOrderItem[]; total_estimado:number; fecha_solicitud:string; fecha_completada:string|null; }
export interface LabOrderCreate { consulta_id:number; indicaciones:string|null; prioridad:string; items:{tipo_examen_id:number;observaciones:string|null;}[]; }

export interface InvoiceItem { detalle_factura_id:number; tipo_servicio:string; descripcion:string; cantidad:number; precio_unitario:number; subtotal:number; }
export interface Payment { pago_id:number; monto:number; metodo_pago:string; referencia:string|null; observaciones:string|null; estado:string; fecha_pago:string; }
export interface Invoice { factura_id:number; numero_factura:string; paciente_id:number; numero_expediente:string; paciente_nombre:string; consulta_id:number|null; nit:string; nombre_facturacion:string; direccion_facturacion:string|null; subtotal:number; descuento:number; total:number; total_pagado:number; saldo_pendiente:number; estado:string; observaciones:string|null; motivo_anulacion:string|null; items:InvoiceItem[]; pagos:Payment[]; fecha_emision:string; fecha_actualizacion:string; }
export interface InvoiceCreate { paciente_id:number; consulta_id:number|null; nit:string; nombre_facturacion:string; direccion_facturacion:string|null; descuento:number; observaciones:string|null; items:{tipo_servicio:string;descripcion:string;cantidad:number;precio_unitario:number;}[]; }
export interface BillingSummary { total_facturado:number; total_pagado:number; saldo_pendiente:number; facturas_pendientes:number; facturas_parciales:number; facturas_pagadas:number; }

export interface AuditLog { bitacora_id:number; usuario_id:number|null; nombre_usuario:string|null; accion:string; modulo:string; metodo_http:string; ruta:string; codigo_respuesta:number; exitoso:boolean; direccion_ip:string|null; duracion_ms:number; detalle:string|null; fecha_evento:string; }
