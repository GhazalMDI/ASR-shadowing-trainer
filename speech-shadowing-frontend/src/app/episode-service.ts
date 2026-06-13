import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from './environments/environment';

@Injectable({
  providedIn: 'root',
})
export class EpisodeService {
private url = `${environment.apiUrl}/episodes/`;

  constructor(private http: HttpClient) { }

  getEpisodeList() {
    return this.http.get(`${this.url}`)
  }
  getEpisodeById(id:string){
    return this.http.get(`${this.url}${id}`)
  }


}
2