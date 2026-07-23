import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthSession } from './models';
const KEY='hms_session';
@Injectable({providedIn:'root'})
export class AuthService {
  private http=inject(HttpClient); private router=inject(Router);
  private state=signal<AuthSession|null>(this.restore());
  readonly session=this.state.asReadonly();
  readonly authenticated=computed(()=>this.state()!==null);
  readonly username=computed(()=>this.state()?.usuario??'');
  readonly roles=computed(()=>this.state()?.roles??[]);
  login(username:string,password:string):Observable<AuthSession>{
    const body=new HttpParams().set('username',username).set('password',password);
    return this.http.post<AuthSession>(`${environment.apiUrl}/auth/login`,body.toString(),{headers:{'Content-Type':'application/x-www-form-urlencoded'}})
      .pipe(tap(session=>{localStorage.setItem(KEY,JSON.stringify(session));this.state.set(session);}));
  }
  token():string|null{return this.state()?.access_token??null;}
  logout(redirect=true):void{localStorage.removeItem(KEY);this.state.set(null);if(redirect)void this.router.navigate(['/login']);}
  private restore():AuthSession|null{try{const value=localStorage.getItem(KEY);return value?JSON.parse(value) as AuthSession:null;}catch{localStorage.removeItem(KEY);return null;}}
}
