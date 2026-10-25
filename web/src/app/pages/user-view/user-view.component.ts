import { Component, DestroyRef, OnInit, ChangeDetectionStrategy, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { ConfirmDialogComponent } from '../../dialogs/confirm-dialog/confirm-dialog.component';
import { ChangePasswordDialogComponent } from '../../dialogs/change-password-dialog/change-password-dialog.component';
import { AuthenticationService } from '../../services/authentication.service';
import { ServerService } from '../../services/server.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { InlineEditComponent } from '../../components/inline-edit/inline-edit.component';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { User } from '../../models';

@Component({
	selector: 'app-user-view',
	templateUrl: './user-view.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./user-view.component.scss'],
	imports: [BreadcrumbComponent, InlineEditComponent, MatButton, MatIcon]
})
export class UserViewComponent implements OnInit {
	auth = inject(AuthenticationService);
	private server = inject(ServerService);
	private dialog = inject(MatDialog);
	private router = inject(Router);
	private route = inject(ActivatedRoute);
	private destroyRef = inject(DestroyRef);

	public username!: string;
	public user?: User;

	ngOnInit(): void {
		// reused when going from another user's page to your own via the header
		this.route.paramMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(params => {
			this.username = params.get('username')!;
			this.loadUser();
		});
	}

	private loadUser() {
		this.server.getUser(this.username).subscribe({
			next: (user) => {
				this.user = user;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public isSelf() {
		return this.auth.getUsername() == this.username;
	}

	public changedValue(property: 'email' | 'isAdmin', newValue: any) {
		this.server.updateUser(this.username, property, newValue).subscribe({
			next: (user) => {
				this.user = user;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public changePassword() {
		this.dialog.open(ChangePasswordDialogComponent, {
			data: {
				username: this.username
			}
		});
	}

	public deleteUser() {
		const self = this.isSelf();
		let text = "This will remove user '" + this.username + "'";
		if(self) {
			text += " (yourself!)"
		}
		text += ". This action is not reversible. Are you really sure?";

		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Delete User",
				text: text,
				action: this.server.deleteUser(this.username)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				if(self) {
					this.auth.logout();
				} else {
					this.router.navigate(['/users']);
				}
			}
		});
	}

	public impersonate() {
		this.auth.impersonate(this.username).subscribe({
			next: () => {
				window.location.reload();
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}
}
