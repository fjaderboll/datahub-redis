import { Injectable, inject } from '@angular/core';
import { UtilsService } from './utils.service';
import { Router } from '@angular/router';
import { ServerService } from './server.service';
import { tap } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { Token } from '../models';

// setTimeout fires immediately for longer delays (about 24.8 days)
const MAX_TIMEOUT = 2 ** 31 - 1;

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
	private server = inject(ServerService);
	private utils = inject(UtilsService);
	private router = inject(Router);
	private dialog = inject(MatDialog);

	private token: string | null = null;
	private username: string | null = null;
	private admin: boolean = false;
	private expire: string | null = null;
	private expireTimer?: ReturnType<typeof setTimeout>;

	constructor() {
		const token = localStorage.getItem('token');
		const username = localStorage.getItem('username');
		const expire = localStorage.getItem('expire');

		if(token && username && !this.hasExpired(expire)) {
			this.setSession(token, username, localStorage.getItem('admin') == "true", expire);
		} else {
			this.clearSession();
		}
	}

	public login(username: string, password: string) {
		return this.server.login(username, password).pipe(
			tap(t => this.startSession(t))
		);
	}

	public impersonate(username: string) {
		return this.server.impersonate(username).pipe(
			tap(t => this.startSession(t))
		);
	}

	private startSession(t: Token) {
		this.setSession(t.token, t.username, t.isAdmin, t.expire);
	}

	private setSession(token: string, username: string, isAdmin: boolean, expire: string | null) {
		this.token = token;
		this.username = username;
		this.admin = isAdmin;
		this.expire = expire;

		localStorage.setItem('token', token);
		localStorage.setItem('username', username);
		localStorage.setItem('admin', isAdmin + "");
		if(expire) {
			localStorage.setItem('expire', expire);
		} else {
			localStorage.removeItem('expire'); // never expires, don't keep the previous session's time
		}

		this.scheduleExpire();
	}

	private clearSession() {
		clearTimeout(this.expireTimer);
		this.token = null;
		this.username = null;
		this.admin = false;
		this.expire = null;
		['token', 'username', 'admin', 'expire'].forEach(key => localStorage.removeItem(key));
	}

	private scheduleExpire() {
		clearTimeout(this.expireTimer);
		if(this.expire) {
			const delay = new Date(this.expire).getTime() - Date.now();
			this.expireTimer = setTimeout(() => {
				if(this.hasExpired(this.expire)) {
					this.sessionExpired();
				} else {
					this.scheduleExpire();
				}
			}, Math.min(Math.max(delay, 0), MAX_TIMEOUT));
		}
	}

	private hasExpired(expire: string | null) {
		return !!expire && new Date(expire).getTime() <= Date.now();
	}

	/** Called when the token has expired or the backend rejects it. */
	public sessionExpired() {
		if(this.isLoggedIn()) {
			this.clearSession();
			this.dialog.closeAll();
			this.utils.toastWarn("Your session has expired, please sign in again.");
			this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
		}
	}

	public getToken() {
		return this.token;
	}

	public isLoggedIn() {
		return !!this.token;
	}

	public logout() {
		const token = this.token;
		const username = this.username;

		this.clearSession();
		this.dialog.closeAll();
		this.router.navigate(['/login']);

		if(token && username) {
			// revoke the token, signed out locally either way
			this.server.logout(username, token).subscribe({
				next: () => this.utils.toastSuccess("Signed out"),
				error: () => this.utils.toastSuccess("Signed out")
			});
		}
	}

	public isAdmin() {
		return this.isLoggedIn() && this.admin;
	}

	public getUsername() {
		return this.username;
	}

}
