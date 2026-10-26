import { Injectable, inject } from '@angular/core';
import { EMPTY, defer, share, tap } from 'rxjs';
import { AuthenticationService } from './authentication.service';
import { ServerService } from './server.service';

/**
 * Readings in the user's datasets as they are created. All subscribers share one connection,
 * opened by the first one and closed when the last one unsubscribes.
 */
@Injectable({
  providedIn: 'root'
})
export class LiveReadingsService {
	private auth = inject(AuthenticationService);
	private server = inject(ServerService);

	public readings$ = defer(() => {
		const token = this.auth.getToken();
		return token ? this.server.streamReadings(token) : EMPTY;
	}).pipe(
		// before share, so the user is told once however many listen
		tap({
			error: (e) => {
				if(e.status === 401) {
					this.auth.sessionExpired();
				} else {
					this.server.showHttpError(e);
				}
			}
		}),
		share()
	);
}
