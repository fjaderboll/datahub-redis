import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { ServerService } from '../../services/server.service';
import { NAME_PATTERN, UtilsService } from '../../services/utils.service';
import { MatFormField, MatLabel, MatHint, MatError } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';

@Component({
	selector: 'app-create-sensor-dialog',
	templateUrl: './create-sensor-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./create-sensor-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, MatFormField, MatLabel, MatHint, MatError, MatInput, FormsModule, MatDialogActions, MatButton, MatDialogClose, MatIcon]
})
export class CreateSensorDialogComponent {
	dialogRef = inject<MatDialogRef<CreateSensorDialogComponent>>(MatDialogRef);
	private server = inject(ServerService);
	private utils = inject(UtilsService);
	data = inject<{ datasetName: string, nodeName: string }>(MAT_DIALOG_DATA);

	public readonly namePattern = NAME_PATTERN;
	public name: string = "";
	public description: string = "";
	public unit: string = "";
	public busy = false;

	public create() {
		this.busy = true;
		this.server.createSensor(this.data.datasetName, this.data.nodeName, this.name, this.description, this.unit).subscribe({
			next: (v) => {
				this.utils.toastSuccess("Created sensor '" + v.name + "'");
				this.dialogRef.close(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
				this.busy = false;
			}
		});
	}
}
