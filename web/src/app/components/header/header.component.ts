import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthenticationService } from 'src/app/services/authentication.service';
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
		public auth: AuthenticationService
	) { }

  	ngOnInit(): void {
  	}

	/*public showLoginLink() {
		return !this.auth.isLoggedIn() && this.router.url != '/login';
	}*/

	public logout() {
		this.auth.logout();
		this.router.navigate(['/login']);
		this.utils.toastSuccess("Signed out");
	}

}
