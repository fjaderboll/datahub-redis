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

	constructor(
		private router: Router,
		public auth: AuthenticationService,
		private server: ServerService,
		public utils: UtilsService
	) { }

	ngOnInit(): void {
  	}

	public showTimeseries() {
		this.router.navigate(['/timeseries']);
	}

}
