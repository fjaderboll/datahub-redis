import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { MatFormField, MatLabel, MatHint, MatError, MatSuffix } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';

@Component({
	selector: 'app-create-token-dialog',
	templateUrl: './create-token-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./create-token-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, MatFormField, MatLabel, MatHint, MatError, MatSuffix, MatInput, FormsModule, MatDialogActions, MatButton, MatDialogClose, MatIcon]
})
export class CreateTokenDialogComponent {
	dialogRef = inject<MatDialogRef<CreateTokenDialogComponent>>(MatDialogRef);
	private server = inject(ServerService);
	utils = inject(UtilsService);

	public description: string = "";
	public ttl: number | null = null;
	public busy = false;

	public create() {
		this.busy = true;
		this.server.createToken(this.description, this.ttl || 0).subscribe({
			next: (v) => {
				this.utils.toastSuccess('Token created');
				this.dialogRef.close(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
				this.busy = false;
			}
		});
	}

}
