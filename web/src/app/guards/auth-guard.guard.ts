import { inject } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivateFn, Router, RouterStateSnapshot } from '@angular/router';
import { AuthenticationService } from '../services/authentication.service';
import { UtilsService } from '../services/utils.service';

export const authGuardGuard: CanActivateFn = (
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ) =>
{
    const auth = inject(AuthenticationService);
    const utils = inject(UtilsService);
    const router = inject(Router);

    if(!auth.isLoggedIn()) {
        utils.toastError("Unauthorized, please login");
        router.navigate(["login"]);
        return false;
    }
    return true;
};
