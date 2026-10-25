import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { ServerService } from '../../services/server.service';
import { NAME_PATTERN, UtilsService } from '../../services/utils.service';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';

@Component({
	selector: 'app-share-dataset-dialog',
	templateUrl: './share-dataset-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./share-dataset-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, MatFormField, MatLabel, MatError, MatInput, FormsModule, MatDialogActions, MatButton, MatDialogClose, MatIcon]
})
export class ShareDatasetDialogComponent {
	dialogRef = inject<MatDialogRef<ShareDatasetDialogComponent>>(MatDialogRef);
	private server = inject(ServerService);
	private utils = inject(UtilsService);
	data = inject<{ datasetName: string }>(MAT_DIALOG_DATA);

	public readonly namePattern = NAME_PATTERN;
	public username: string = "";
	public busy = false;

	public share() {
		this.busy = true;
		this.server.shareDataset(this.data.datasetName, this.username).subscribe({
			next: () => {
				this.utils.toastSuccess("Shared dataset with '" + this.username + "'");
				this.dialogRef.close(this.username);
			},
			error: (e) => {
				this.server.showHttpError(e);
				this.busy = false;
			}
		});
	}
}
