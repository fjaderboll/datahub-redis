import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.component.html',
  styleUrls: ['./confirm-dialog.component.scss']
})
export class ConfirmDialogComponent implements OnInit {
	public inputData: any;

	constructor(
		public dialogRef: MatDialogRef<ConfirmDialogComponent>,
		private server: ServerService,
		private utils: UtilsService,
		@Inject(MAT_DIALOG_DATA) public data: any
	) {
		this.inputData = data;
	}

	ngOnInit(): void {
	}

	public apply() {
		this.inputData.action.subscribe({
			next: (v: any) => {
				this.utils.toastSuccess(v);
				this.dialogRef.close(v);
			},
			error: (e: any) => {
				this.server.showHttpError(e);
			}
		});
	}
}
