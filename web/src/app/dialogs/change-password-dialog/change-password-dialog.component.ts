import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { MatFormField, MatLabel, MatHint, MatSuffix } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatIcon } from '@angular/material/icon';
import { MatButton, MatIconButton } from '@angular/material/button';

@Component({
	selector: 'app-change-password-dialog',
	templateUrl: './change-password-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./change-password-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, MatFormField, MatLabel, MatHint, MatInput, FormsModule, MatIcon, MatSuffix, MatDialogActions, MatButton, MatIconButton, MatDialogClose]
})
export class ChangePasswordDialogComponent {
	dialogRef = inject<MatDialogRef<ChangePasswordDialogComponent>>(MatDialogRef);
	private server = inject(ServerService);
	private utils = inject(UtilsService);
	data = inject<{ username: string }>(MAT_DIALOG_DATA);

	public showPassword: boolean = false;
	public password1: string = "";
	public password2: string = "";
	public busy = false;

	public change() {
		this.busy = true;
		this.server.updateUser(this.data.username, 'password', this.password1).subscribe({
			next: () => {
				this.utils.toastSuccess("Password changed");
				this.dialogRef.close(true);
			},
			error: (e) => {
				this.server.showHttpError(e);
				this.busy = false;
			}
		});
	}
}
