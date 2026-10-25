import { TestBed } from '@angular/core/testing';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { authInterceptor } from './auth.interceptor';
import { AuthenticationService } from './authentication.service';
import { environment } from '../../environments/environment';

describe('authInterceptor', () => {
	const datasetsUrl = environment.apiUrl + 'datasets/';
	let http: HttpClient;
	let controller: HttpTestingController;

	beforeEach(() => {
		localStorage.clear();
		localStorage.setItem('token', 'abc');
		localStorage.setItem('username', 'admin');

		TestBed.configureTestingModule({
			providers: [
				provideRouter([{ path: 'login', children: [] }]),
				provideHttpClient(withInterceptors([authInterceptor])),
				provideHttpClientTesting()
			]
		});
		http = TestBed.inject(HttpClient);
		controller = TestBed.inject(HttpTestingController);
	});

	afterEach(() => {
		controller.verify();
	});

	it('adds the token to API requests only', () => {
		http.get(datasetsUrl).subscribe();
		http.get('assets/img/logo/logo.svg', { responseType: 'text' }).subscribe();

		expect(controller.expectOne(datasetsUrl).request.headers.get('Authorization')).toBe('Bearer abc');
		expect(controller.expectOne('assets/img/logo/logo.svg').request.headers.has('Authorization')).toBe(false);
	});

	it('ends the session when the backend rejects the token', () => {
		const auth = TestBed.inject(AuthenticationService);
		expect(auth.isLoggedIn()).toBe(true);

		http.get(datasetsUrl).subscribe({ error: () => {} });
		controller.expectOne(datasetsUrl).flush({ message: 'Unauthorized' }, { status: 401, statusText: 'Unauthorized' });

		expect(auth.isLoggedIn()).toBe(false);
	});
});
