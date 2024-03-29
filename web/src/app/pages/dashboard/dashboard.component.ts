import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-dashboard',
	templateUrl: './dashboard.component.html',
	styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
	private startTime = new Date().getTime();
	public receivedReadings = 0;
	public receivedReadingsPerSecond: number = 0.0;
	public lastReadings: any = [];
	public streamingReadings = false;

	constructor(
		private router: Router,
		public auth: AuthenticationService,
		private server: ServerService,
		public utils: UtilsService
	) { }

	ngOnInit(): void {
		this.streamReadings();
  	}

	public streamReadings() {
		this.streamingReadings = true;
		this.server.getStateReadings().subscribe({
			next: (v: any) => {
				if(v.partialText) {
					const t = v.partialText.trim();
					const i = t.lastIndexOf('\n');
					const json = t.substring(i);
					const reading = JSON.parse(json);
					this.handleReading(reading);
				}
			},
			error: (e) => {
				this.server.showHttpError(e);
				this.streamingReadings = false;
			}
		});
	}

	private handleReading(reading: any) {
		this.receivedReadings++;
		this.receivedReadingsPerSecond = this.receivedReadings / ((new Date().getTime() - this.startTime) / 1000);

		this.lastReadings.push(reading);
		if(this.lastReadings.length > 10) {
			this.lastReadings.shift();
		}
	}

}
