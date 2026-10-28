import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ActivatedRouteSnapshot, CanActivateFn, Router, RouterStateSnapshot, UrlTree, provideRouter } from '@angular/router';
import { adminGuard, authGuard } from './auth.guard';

describe('guards', () => {
	function setup(session?: { admin: boolean }) {
		localStorage.clear();
		if(session) {
			localStorage.setItem('token', 'abc');
			localStorage.setItem('username', 'someone');
			localStorage.setItem('admin', String(session.admin));
		}
		TestBed.configureTestingModule({
			providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()]
		});
	}

	function run(guard: CanActivateFn, url: string) {
		return TestBed.runInInjectionContext(() => guard({} as ActivatedRouteSnapshot, { url } as RouterStateSnapshot));
	}

	function serialize(result: unknown) {
		return TestBed.inject(Router).serializeUrl(result as UrlTree);
	}

	it('sends visitors to the login page, and back afterwards', () => {
		setup();
		expect(serialize(run(authGuard, '/datasets/home'))).toBe('/login?returnUrl=%2Fdatasets%2Fhome');
	});

	it('lets signed in users through', () => {
		setup({ admin: false });
		expect(run(authGuard, '/datasets')).toBe(true);
	});

	it('keeps others out of administration pages', () => {
		setup({ admin: false });
		expect(serialize(run(adminGuard, '/settings'))).toBe('/');
	});

	it('lets administrators in', () => {
		setup({ admin: true });
		expect(run(adminGuard, '/settings')).toBe(true);
	});
});
