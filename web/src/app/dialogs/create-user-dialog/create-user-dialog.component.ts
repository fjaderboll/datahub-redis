import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { ServerService } from '../../services/server.service';
import { NAME_PATTERN, UtilsService } from '../../services/utils.service';
import { MatFormField, MatLabel, MatHint, MatError, MatSuffix } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatIcon } from '@angular/material/icon';
import { MatButton, MatIconButton } from '@angular/material/button';

@Component({
	selector: 'app-create-user-dialog',
	templateUrl: './create-user-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./create-user-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, MatFormField, MatLabel, MatHint, MatError, MatInput, FormsModule, MatIcon, MatSuffix, MatDialogActions, MatButton, MatIconButton, MatDialogClose]
})
export class CreateUserDialogComponent {
	dialogRef = inject<MatDialogRef<CreateUserDialogComponent>>(MatDialogRef);
	private server = inject(ServerService);
	private utils = inject(UtilsService);

	public readonly namePattern = NAME_PATTERN;
	public showPassword: boolean = false;
	public username: string = "";
	public password1: string = "";
	public password2: string = "";
	public busy = false;

	public create() {
		this.busy = true;
		this.server.createUser(this.username, this.password1).subscribe({
			next: (v) => {
				this.utils.toastSuccess("Created user '" + v.username + "'");
				this.dialogRef.close(v.username);
			},
			error: (e) => {
				this.server.showHttpError(e);
				this.busy = false;
			}
		});
	}
}
