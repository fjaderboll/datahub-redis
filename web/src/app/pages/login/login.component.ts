import { Component, OnInit, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { CreateUserDialogComponent } from '../../dialogs/create-user-dialog/create-user-dialog.component';
import { AuthenticationService } from '../../services/authentication.service';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { environment } from '../../../environments/environment';
import { MatIcon } from '@angular/material/icon';
import { MatFormField, MatLabel, MatSuffix } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatButton, MatIconButton } from '@angular/material/button';

@Component({
	selector: 'app-login',
	templateUrl: './login.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./login.component.scss'],
	imports: [MatIcon, MatFormField, MatLabel, MatInput, FormsModule, MatSuffix, MatButton, MatIconButton]
})
export class LoginComponent implements OnInit {
	private router = inject(Router);
	private route = inject(ActivatedRoute);
	private dialog = inject(MatDialog);
	auth = inject(AuthenticationService);
	private server = inject(ServerService);
	private utils = inject(UtilsService);

	public showPassword: boolean = false;
	public username: string = "";
	public password: string = "";
	public createFirstUserRequired = false;
	public allowPublicCreateUser = false;
	public setupError = false;
	public busy = false;
	public apiUrl = environment.apiUrl;

	ngOnInit(): void {
		if(this.auth.isLoggedIn()) {
			this.router.navigateByUrl(this.getReturnUrl());
			return;
		}
		this.loadState();
	}

	public loadState() {
		this.server.getStateUsers().subscribe({
			next: (v) => {
				this.createFirstUserRequired = v.createFirstUserRequired;
				this.allowPublicCreateUser = v.allowPublicCreateUser;
			},
			error: (e) => {
				console.error(e);
				this.setupError = true;
			}
		});
	}

	public login() {
		this.busy = true;
		this.auth.login(this.username, this.password).subscribe({
			next: () => {
				this.router.navigateByUrl(this.getReturnUrl());
				this.utils.toastSuccess("Successfully signed in");
			},
			error: (e) => {
				this.busy = false;
				if(e.status == 401) {
					this.utils.toastError("Invalid credentials");
				} else {
					this.server.showHttpError(e);
				}
			}
		});
	}

	// only paths within the app, never another site
	private getReturnUrl() {
		const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
		if(returnUrl && returnUrl.startsWith('/') && !returnUrl.startsWith('//') && !returnUrl.startsWith('/login')) {
			return returnUrl;
		}
		return '/';
	}

	public register() {
		const dialog = this.dialog.open(CreateUserDialogComponent);
		dialog.afterClosed().subscribe(newUsername => {
			if(newUsername) {
				this.username = newUsername;
				this.password = "";
				this.loadState();
			}
		});
	}
}
