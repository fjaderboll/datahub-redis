import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { MatFormField, MatLabel, MatHint } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';

@Component({
	selector: 'app-create-reading-dialog',
	templateUrl: './create-reading-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./create-reading-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, MatFormField, MatLabel, MatHint, MatInput, FormsModule, MatDialogActions, MatButton, MatDialogClose, MatIcon]
})
export class CreateReadingDialogComponent {
	dialogRef = inject<MatDialogRef<CreateReadingDialogComponent>>(MatDialogRef);
	private server = inject(ServerService);
	private utils = inject(UtilsService);
	data = inject<{ datasetName: string, nodeName: string, sensorName: string }>(MAT_DIALOG_DATA);

	public value: number | null = null;
	public time: string = "";
	public busy = false;

	public create() {
		this.busy = true;
		this.server.createReading(this.data.datasetName, this.data.nodeName, this.data.sensorName, this.value!, this.time.trim() || null).subscribe({
			next: (v) => {
				this.utils.toastSuccess('Reading created');
				this.dialogRef.close(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
				this.busy = false;
			}
		});
	}

}
