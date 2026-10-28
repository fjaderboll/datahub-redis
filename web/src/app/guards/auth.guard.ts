import { inject } from '@angular/core';
import { CanActivateFn, Router, RouterStateSnapshot } from '@angular/router';
import { AuthenticationService } from '../services/authentication.service';

export const authGuard: CanActivateFn = (route, state) => {
	const auth = inject(AuthenticationService);

	if(!auth.isLoggedIn()) {
		return loginPage(state);
	}
	return true;
};

export const adminGuard: CanActivateFn = (route, state) => {
	const auth = inject(AuthenticationService);

	if(!auth.isLoggedIn()) {
		return loginPage(state);
	}
	if(!auth.isAdmin()) {
		return inject(Router).createUrlTree(['/']);
	}
	return true;
};

// come back to the requested page after signing in
function loginPage(state: RouterStateSnapshot) {
	const queryParams = (state.url === '/' ? {} : { returnUrl: state.url });
	return inject(Router).createUrlTree(['/login'], { queryParams });
}
