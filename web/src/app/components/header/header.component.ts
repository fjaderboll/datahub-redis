import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
	public apiUrl: string = "";

	constructor(
		private router: Router,
		private utils: UtilsService,
		public auth: AuthenticationService,
        private server: ServerService
	) { }

  	ngOnInit(): void {
		this.apiUrl = environment.apiUrl;
  	}

	/*public showLoginLink() {
		return !this.auth.isLoggedIn() && this.router.url != '/login';
	}*/

	public logout() {
        this.auth.logout(true);
	}

}
