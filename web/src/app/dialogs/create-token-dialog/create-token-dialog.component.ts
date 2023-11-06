import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-create-token-dialog',
  templateUrl: './create-token-dialog.component.html',
  styleUrls: ['./create-token-dialog.component.scss']
})
export class CreateTokenDialogComponent implements OnInit {
	public description: string = "";
    public ttl: number | null = null;

	constructor(
		public dialogRef: MatDialogRef<CreateTokenDialogComponent>,
		private server: ServerService,
		private utils: UtilsService
	) { }

	ngOnInit(): void {
	}

    public isFormValid() {
        return this.ttl == null || this.ttl > 0;
	}

  	public create() {
		this.server.createToken(this.description, this.ttl).subscribe({
			next: (v: any) => {
				this.utils.toastSuccess('Token created');
				this.dialogRef.close(v);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

}
