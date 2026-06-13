import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {  of, tap } from 'rxjs';
import { environment } from './environments/environment'

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private base_url = `${environment.apiUrl}/dashboard`;

  private userCache: any | null = null

  constructor(private http: HttpClient) { }
  getUserInfo(force=false) {
    if (this.userCache && !force){
      return of(this.userCache)
    }
    return this.http.get(`${this.base_url}/information`).pipe(
      tap(user=> this.userCache=user)
    );

  }
  getPerformance() {
    return this.http.get(`${this.base_url}/performance`)
  }

  clearChache(){
    this.userCache = null;
  }

}
