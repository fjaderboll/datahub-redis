import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { ServerService } from '../../services/server.service';
import { NAME_PATTERN, UtilsService } from '../../services/utils.service';
import { MatFormField, MatLabel, MatHint, MatError } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';

@Component({
	selector: 'app-create-dataset-dialog',
	templateUrl: './create-dataset-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./create-dataset-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, MatFormField, MatLabel, MatHint, MatError, MatInput, FormsModule, MatDialogActions, MatButton, MatDialogClose, MatIcon]
})
export class CreateDatasetDialogComponent {
	dialogRef = inject<MatDialogRef<CreateDatasetDialogComponent>>(MatDialogRef);
	private server = inject(ServerService);
	private utils = inject(UtilsService);

	public readonly namePattern = NAME_PATTERN;
	public name: string = "";
	public description: string = "";
	public busy = false;

	public create() {
		this.busy = true;
		this.server.createDataset(this.name, this.description).subscribe({
			next: (v) => {
				this.utils.toastSuccess("Created dataset '" + v.name + "'");
				this.dialogRef.close(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
				this.busy = false;
			}
		});
	}
}
