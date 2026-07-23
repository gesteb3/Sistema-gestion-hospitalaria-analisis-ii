import { HttpErrorResponse } from '@angular/common/http';
export function apiError(error:unknown,fallback='No fue posible completar la operación.'):string{
  if(!(error instanceof HttpErrorResponse))return fallback;
  const detail=error.error?.detail;
  if(typeof detail==='string')return detail;
  if(Array.isArray(detail))return detail.map((x:{msg?:string})=>x.msg).filter(Boolean).join(' ');
  if(error.status===0)return 'No se pudo conectar con FastAPI. Verificá que el backend esté activo.';
  return fallback;
}
