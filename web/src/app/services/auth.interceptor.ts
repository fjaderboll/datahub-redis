import { inject } from '@angular/core';
import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthenticationService } from './authentication.service';

/**
 * Adds the session token to API requests, and ends the session if the
 * backend no longer accepts it (expired, revoked or user removed).
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
	const auth = inject(AuthenticationService);
	const token = auth.getToken();

	if(token && req.url.startsWith(environment.apiUrl) && !req.headers.has('Authorization')) {
		req = req.clone({ setHeaders: { Authorization: 'Bearer ' + token } });
	}

	return next(req).pipe(
		catchError((e: unknown) => {
			if(e instanceof HttpErrorResponse && e.status === 401) {
				auth.sessionExpired();
			}
			return throwError(() => e);
		})
	);
};
