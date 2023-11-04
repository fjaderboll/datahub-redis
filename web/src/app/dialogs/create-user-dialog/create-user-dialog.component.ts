import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-create-user-dialog',
  templateUrl: './create-user-dialog.component.html',
  styleUrls: ['./create-user-dialog.component.scss']
})
export class CreateUserDialogComponent implements OnInit {
	public showPassword: boolean = false;
	public username: string = "";
	public password1: string = "";
	public password2: string = "";

	constructor(
		public dialogRef: MatDialogRef<CreateUserDialogComponent>,
		private server: ServerService,
		private utils: UtilsService
	) { }

	ngOnInit(): void {
	}

	public isFormValid() {
		return this.username.length * this.password1.length * this.password2.length > 0 && this.password1 == this.password2;
	}

	public create() {
		this.server.createUser(this.username, this.password1).subscribe({
			next: (v: any) => {
				this.utils.toastSuccess("Created user '" + v.username + "'");
                this.dialogRef.close(v.username);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}
}
