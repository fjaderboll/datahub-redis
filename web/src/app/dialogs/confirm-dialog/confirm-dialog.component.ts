import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { Observable } from 'rxjs';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';

export interface ConfirmDialogData {
	title: string;
	text: string;
	/** Run when confirmed, emitting the message to show */
	action: Observable<string>;
}

@Component({
	selector: 'app-confirm-dialog',
	templateUrl: './confirm-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./confirm-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, MatDialogActions, MatButton, MatDialogClose, MatIcon]
})
export class ConfirmDialogComponent {
	dialogRef = inject<MatDialogRef<ConfirmDialogComponent>>(MatDialogRef);
	private server = inject(ServerService);
	private utils = inject(UtilsService);
	data = inject<ConfirmDialogData>(MAT_DIALOG_DATA);

	public busy = false;

	public apply() {
		this.busy = true;
		this.data.action.subscribe({
			next: (message) => {
				this.utils.toastSuccess(message);
				this.dialogRef.close(true);
			},
			error: (e) => {
				this.server.showHttpError(e);
				this.busy = false;
			}
		});
	}
}
