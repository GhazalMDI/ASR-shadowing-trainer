import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { first, Observable } from 'rxjs';
import { observableToBeFn } from 'rxjs/internal/testing/TestScheduler';
import { environment } from './environments/environment';
@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private base_url = `${environment.apiUrl}/accounts`;
 constructor(private http:HttpClient){}
 
 setToken(access:string,refresh:string):void{
  localStorage.setItem("accessToken",access);
  localStorage.setItem("refreshToken",refresh);
 }
 getAccessToken():string | null{
    return localStorage.getItem('accessToken');
  }
 getRefreshToken():string | null{
    return localStorage.getItem('refreshToken');
  }
 register(first_name:string,last_name:string,email:string,password:string):Observable<any>{
  const url = `${this.base_url}/register`;
  return this.http.post(url,{first_name:first_name,last_name:last_name,email:email,password:password});
 }

 login(email:string,password:string):Observable<any>{
  const url = `${this.base_url}/login`;
   return this.http.post(url,{email:email,password:password});
 }
logOut(refreshToken: string) {
  const url = `${this.base_url}/logout`;
  console.log(this.getAccessToken())
  return this.http.post(url, {
    body: { refresh_token: refreshToken },
    headers: {
      Authorization: `Bearer ${this.getAccessToken()}`
    }
  });
}

}
