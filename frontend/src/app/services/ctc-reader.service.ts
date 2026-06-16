import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ResponseLeituraCTC } from '../models/ctc.model';

@Injectable({ providedIn: 'root' })
export class CtcReaderService {
  constructor(private http: HttpClient) { }

  lerCTC(file: File): Observable<ResponseLeituraCTC> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<ResponseLeituraCTC>(
      `${environment.apiUrl}/leCTC`,
      formData
    );
  }
}
