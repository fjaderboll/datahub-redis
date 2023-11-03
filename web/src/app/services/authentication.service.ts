import { Injectable } from '@angular/core';
import { UtilsService } from './utils.service';
import { Router } from '@angular/router';
import { ServerService } from './server.service';
import { Observable } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
	private token: string | null = null;
	private username: string | null = null;
	private admin: boolean = false;
	private expireTimer: any;

	constructor(
		public server: ServerService,
		private utils: UtilsService,
		private router: Router,
		private dialog: MatDialog
	) {
		this.setToken(
			localStorage.getItem('token'),
			localStorage.getItem('username'),
			localStorage.getItem('admin') == "true",
			localStorage.getItem('expire')
		);
	}

	public login(username: string, password: string) {
		return new Observable(
			observer => {
				this.server.login(username, password).subscribe({
					next: (v: any) => {
						this.setToken(v.token, v.username, v.isAdmin, v.expire);
						observer.next(v);
					},
					error: (e) => {
						observer.error(e);
					},
					complete: () => {
						observer.complete();
					}
				});
			}
		);
	}

	public impersonate(username: string) {
		return new Observable(
			observer => {
				this.server.impersonate(username).subscribe({
					next: (v: any) => {
						this.setToken(v.token, v.username, v.isAdmin, v.expire);
						observer.next(v);
					},
					error: (e) => {
						observer.error(e);
					},
					complete: () => {
						observer.complete();
					}
				});
			}
		);
	}

	public setToken(token: string | null, username: string | null, isAdmin: boolean, expire: string | null) {
		if(token && token.length > 0 && username && username.length > 0) {
			this.token = token;
			this.username = username;
			this.admin = isAdmin;
			localStorage.setItem('token', this.token);
			localStorage.setItem('username', this.username);
			localStorage.setItem('admin', this.admin + "");
			this.server.setToken(this.token);
			if(expire) {
				localStorage.setItem('expire', expire);
				this.expireTimer = setTimeout(() => {
					this.logout();
					this.dialog.closeAll();
					this.router.navigate(['/login']);
					this.utils.toastWarn("You session has expired, please sign in again.");
				}, new Date(expire).getTime() - new Date().getTime());
			}
		} else {
			this.token = null;
			localStorage.removeItem('token');
			this.server.setToken("");
		}
	}

	public getToken() {
		return this.token;
	}

	public isLoggedIn() {
		return !!this.token;
	}

	public logout() {
		this.setToken(null, this.username, this.admin, null);
		if(this.expireTimer) {
			clearTimeout(this.expireTimer);
			this.expireTimer = null;
		}
	}

	public isAdmin() {
		return this.isLoggedIn() && this.admin;
	}

	public getUsername() {
		return this.username;
	}

}
