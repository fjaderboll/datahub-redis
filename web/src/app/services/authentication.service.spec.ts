import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { AuthenticationService } from './authentication.service';
import { environment } from '../../environments/environment';

const DAY = 24 * 3600 * 1000;

describe('AuthenticationService', () => {
	const api = environment.apiUrl;
	let http: HttpTestingController;

	function createService() {
		TestBed.configureTestingModule({
			providers: [provideRouter([{ path: 'login', children: [] }]), provideHttpClient(), provideHttpClientTesting()]
		});
		http = TestBed.inject(HttpTestingController);
		return TestBed.inject(AuthenticationService);
	}

	function login(auth: AuthenticationService, expire: string | null) {
		auth.login('admin', 'secret').subscribe();
		http.expectOne(api + 'users/admin/login').flush({ token: 'abc', username: 'admin', isAdmin: true, expire });
	}

	beforeEach(() => {
		localStorage.clear();
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it('restores a stored session', () => {
		localStorage.setItem('token', 'abc');
		localStorage.setItem('username', 'admin');
		localStorage.setItem('admin', 'true');
		localStorage.setItem('expire', new Date(Date.now() + 3600 * 1000).toISOString());

		const auth = createService();
		expect(auth.isLoggedIn()).toBe(true);
		expect(auth.isAdmin()).toBe(true);
		expect(auth.getUsername()).toBe('admin');
	});

	it('does not restore an expired session', () => {
		localStorage.setItem('token', 'abc');
		localStorage.setItem('username', 'admin');
		localStorage.setItem('expire', new Date(Date.now() - 1000).toISOString());

		const auth = createService();
		expect(auth.isLoggedIn()).toBe(false);
		expect(localStorage.getItem('token')).toBeNull();
	});

	it('forgets the previous expire time when the new session never expires', () => {
		localStorage.setItem('expire', new Date(Date.now() - 1000).toISOString());

		const auth = createService();
		login(auth, null);
		expect(auth.isLoggedIn()).toBe(true);
		expect(localStorage.getItem('expire')).toBeNull();
	});

	it('ends the session when it expires, also beyond the longest possible timeout', () => {
		vi.useFakeTimers();
		const auth = createService();
		login(auth, new Date(Date.now() + 40 * DAY).toISOString());

		vi.advanceTimersByTime(30 * DAY);
		expect(auth.isLoggedIn()).toBe(true);

		vi.advanceTimersByTime(11 * DAY);
		expect(auth.isLoggedIn()).toBe(false);
		expect(localStorage.getItem('token')).toBeNull();
	});

	it('signs out locally and revokes the token', () => {
		const auth = createService();
		login(auth, null);

		auth.logout();
		expect(auth.isLoggedIn()).toBe(false);
		expect(localStorage.getItem('token')).toBeNull();

		const req = http.expectOne(api + 'users/admin/logout');
		expect(req.request.headers.get('Authorization')).toBe('Bearer abc');
		req.flush("Token invalidated");
	});
});
