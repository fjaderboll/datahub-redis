import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-create-sensor-dialog',
	templateUrl: './create-sensor-dialog.component.html',
	styleUrls: ['./create-sensor-dialog.component.scss']
})
export class CreateSensorDialogComponent implements OnInit {
	private inputData: any;
    public name: string = "";
	public description: string = "";

	constructor(
		public dialogRef: MatDialogRef<CreateSensorDialogComponent>,
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
		this.server.createSensor(this.inputData.datasetName, this.inputData.nodeName, this.name, this.description).subscribe({
			next: (v: any) => {
				this.utils.toastSuccess("Created sensor '" + v.name + "'");
				this.dialogRef.close(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}
}
