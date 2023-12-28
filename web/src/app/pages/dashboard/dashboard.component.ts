import { Component, OnInit } from '@angular/core';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-dashboard',
	templateUrl: './dashboard.component.html',
	styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {

	constructor(
		public auth: AuthenticationService,
		private server: ServerService,
		public utils: UtilsService
	) { }

	ngOnInit(): void {
		if(this.auth.isAdmin()) {
			this.loadSystem();
		}
  	}

	private loadSystem() {
		this.server.getStateSystem().subscribe({
			next: (v: any) => {
				console.log(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

}
