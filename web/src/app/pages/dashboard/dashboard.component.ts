import { Component, OnInit, OnDestroy, ChangeDetectionStrategy, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthenticationService } from '../../services/authentication.service';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { DecimalPipe } from '@angular/common';
import { SystemMemoryComponent } from '../../components/system-memory/system-memory.component';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { Reading } from '../../models';

@Component({
	selector: 'app-dashboard',
	templateUrl: './dashboard.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./dashboard.component.scss'],
	imports: [SystemMemoryComponent, MatButton, MatIcon, RouterLink, DecimalPipe]
})
export class DashboardComponent implements OnInit, OnDestroy {
	auth = inject(AuthenticationService);
	private server = inject(ServerService);
	utils = inject(UtilsService);

	private startTime = 0;
	private streamSubscription?: Subscription;
	public receivedReadings = 0;
	public receivedReadingsPerSecond: number = 0.0;
	public lastReadings: Reading[] = [];
	public streamingReadings = false;

	ngOnInit(): void {
		this.streamReadings();
	}

	ngOnDestroy(): void {
		this.streamSubscription?.unsubscribe(); // closes the connection
	}

	public streamReadings() {
		const token = this.auth.getToken();
		if(!token) {
			return;
		}

		this.streamingReadings = true;
		this.startTime = Date.now();
		this.receivedReadings = 0;
		this.receivedReadingsPerSecond = 0;

		this.streamSubscription = this.server.streamReadings(token).subscribe({
			next: (reading) => {
				this.handleReading(reading);
			},
			error: (e) => {
				if(e.status === 401) {
					this.auth.sessionExpired();
				} else {
					this.server.showHttpError(e);
				}
				this.streamingReadings = false;
			},
			complete: () => {
				this.streamingReadings = false;
			}
		});
	}

	private handleReading(reading: Reading) {
		this.receivedReadings++;
		this.receivedReadingsPerSecond = this.receivedReadings / ((Date.now() - this.startTime) / 1000);

		this.lastReadings.push(reading);
		if(this.lastReadings.length > 10) {
			this.lastReadings.shift();
		}
	}

}
