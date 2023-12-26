import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-create-reading-dialog',
	templateUrl: './create-reading-dialog.component.html',
	styleUrls: ['./create-reading-dialog.component.scss']
})
export class CreateReadingDialogComponent implements OnInit {
	private inputData: any;
	public value!: number;
    public time: number | null = null;

	constructor(
		public dialogRef: MatDialogRef<CreateReadingDialogComponent>,
		private server: ServerService,
		private utils: UtilsService,
        @Inject(MAT_DIALOG_DATA) public data: any
	) {
		this.inputData = data;
	}

	ngOnInit(): void {
	}

	public isFormValid() {
		return this.value !== undefined && this.value !== null;
	}

  	public create() {
		const time = (this.time ? this.time+"" : null);
		this.server.createReading(this.inputData.datasetName, this.inputData.nodeName, this.inputData.sensorName, this.value, time).subscribe({
			next: (v: any) => {
				this.utils.toastSuccess('Reading created');
				this.dialogRef.close(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

}
