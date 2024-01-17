import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-share-dataset-dialog',
	templateUrl: './share-dataset-dialog.component.html',
	styleUrls: ['./share-dataset-dialog.component.scss']
})
export class ShareDatasetDialogComponent implements OnInit {
	private inputData: any;
    public username: string = "";

	constructor(
		public dialogRef: MatDialogRef<ShareDatasetDialogComponent>,
		private server: ServerService,
		private utils: UtilsService,
        @Inject(MAT_DIALOG_DATA) public data: any
	) {
        this.inputData = data;
    }

	ngOnInit(): void {
	}

	public isFormValid() {
		return this.username.length > 0;
	}

	public share() {
		this.server.shareDataset(this.inputData.datasetName, this.username).subscribe({
			next: (v: any) => {
				this.utils.toastSuccess("Shared dataset with '" + this.username + "'");
				this.dialogRef.close(this.username);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}
}
