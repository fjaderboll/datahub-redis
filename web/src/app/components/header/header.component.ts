import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {

	constructor(
		private router: Router,
		private utils: UtilsService,
		public auth: AuthenticationService,
        private server: ServerService
	) { }

  	ngOnInit(): void {
  	}

	/*public showLoginLink() {
		return !this.auth.isLoggedIn() && this.router.url != '/login';
	}*/

	public logout() {
        this.auth.logout().subscribe({
			next: (v) => {
				this.router.navigate(['/login']);
		        this.utils.toastSuccess("Signed out");
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

}
