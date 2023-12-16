import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-create-dataset-dialog',
  templateUrl: './create-dataset-dialog.component.html',
  styleUrls: ['./create-dataset-dialog.component.scss']
})
export class CreateDatasetDialogComponent implements OnInit {
	public name: string = "";
	public description: string = "";

	constructor(
		public dialogRef: MatDialogRef<CreateDatasetDialogComponent>,
		private server: ServerService,
		private utils: UtilsService
	) { }

	ngOnInit(): void {
	}

	public isFormValid() {
		return this.name.length > 0;
	}

	public create() {
		this.server.createDataset(this.name, this.description).subscribe({
			next: (v: any) => {
				this.utils.toastSuccess("Created dataset '" + v.name + "'");
				this.dialogRef.close(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}
}
