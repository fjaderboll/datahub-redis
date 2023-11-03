import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { ConfirmDialogComponent } from 'src/app/dialogs/confirm-dialog/confirm-dialog.component';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-user-view',
  templateUrl: './user-view.component.html',
  styleUrls: ['./user-view.component.scss']
})
export class UserViewComponent implements OnInit {
	public user: any;

	constructor(
		public auth: AuthenticationService,
		private server: ServerService,
		private dialog: MatDialog,
		private router: Router,
		private route: ActivatedRoute
	) { }

	ngOnInit(): void {
		this.loadUser();
	}

	private loadUser() {
		let username = this.route.snapshot.paramMap.get('username') || 'this should never happen';

		this.server.getUser(username).subscribe({
			next: (user: any) => {
				this.user = user;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public changedValue(property: string, newValue: any) {
		this.server.updateUser(this.user.username, property, newValue).subscribe({
			next: (response: any) => {
				this.user[property] = newValue;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public deleteUser() {
		let text = "This will remove user '" + this.user.username + "'";
		if(this.auth.getUsername() == this.user.username) {
			text += " (yourself!)"
		}
		text += ". This action is not reversible. Are you really sure?";

		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Delete User",
				text: text,
				action: new Observable(
					observer => {
						this.server.deleteUser(this.user.username).subscribe({
							next: (v: any) => {
								observer.next(v);
							},
							error: (e) => {
								observer.error(e);
							},
							complete: () => {
								observer.complete();
							}
						});
					}
				)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				if(this.auth.getUsername() == this.user.username) {
					this.auth.logout();
					this.router.navigate(['/login']);
				} else {
					this.router.navigate(['/users']);
				}
			}
		});
	}

	public impersonate() {
		this.auth.impersonate(this.user.username).subscribe({
			next: (v) => {
				window.location.reload();
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}
}
