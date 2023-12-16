import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
    selector: 'app-create-node-dialog',
	templateUrl: './create-node-dialog.component.html',
	styleUrls: ['./create-node-dialog.component.scss']
})
export class CreateNodeDialogComponent implements OnInit {
	private inputData: any;
    public name: string = "";
	public description: string = "";

	constructor(
		public dialogRef: MatDialogRef<CreateNodeDialogComponent>,
		private server: ServerService,
		private utils: UtilsService,
        @Inject(MAT_DIALOG_DATA) public data: any
	) {
        this.inputData = data;
    }

	ngOnInit(): void {
	}

	public isFormValid() {
		return this.name.length > 0;
	}

	public create() {
		this.server.createNode(this.inputData.datasetName, this.name, this.description).subscribe({
			next: (v: any) => {
				this.utils.toastSuccess("Created node '" + v.name + "'");
				this.dialogRef.close(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}
}
