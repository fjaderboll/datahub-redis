import { Injectable } from '@angular/core';
import { UtilsService } from './utils.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ServerService {
	private apiUrl: string;
	private httpOptionsJson: any;
	private httpOptionsText: any;

	constructor(
		private http: HttpClient,
		private utils: UtilsService
	) {
		this.apiUrl = environment.apiUrl;
	}

	public setToken(token: string) {
		let headers = new HttpHeaders({
			'Content-Type': 'application/json',
			'Authorization': ' Bearer ' + token
		});
		this.httpOptionsJson = {
			headers,
			responseType: 'json'
		};
		this.httpOptionsText = {
			headers,
			responseType: 'text'
		};
	}

	public showHttpError(error: any) {
		console.log(error);
		if(error.error && (typeof error.error === 'string' || error.error instanceof String)) {
			this.utils.toastError(error.error);
		} else {
			this.utils.toastError(error.message);
		}
	}

    public getStateUsers() {
		const url = this.apiUrl + "state/users";
		return this.http.get(url, this.httpOptionsJson);
	}

	public login(username: string, password: string) {
		const url = this.apiUrl + "users/" + username + "/login";
		return this.http.post(url, { password });
	}

	public impersonate(username: string) {
		const url = this.apiUrl + "users/" + username + "/impersonate";
		return this.http.get(url, this.httpOptionsJson);
	}
}
