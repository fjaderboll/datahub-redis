import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { CreateUserDialogComponent } from 'src/app/dialogs/create-user-dialog/create-user-dialog.component';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.scss']
})
export class UserListComponent implements OnInit, AfterViewInit {
	public displayedColumns: string[] = ['username', 'email', 'isAdmin'];
	public dataSource = new MatTableDataSource<any>();

	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

  	constructor(
		public auth: AuthenticationService,
		private server: ServerService,
		private utils: UtilsService,
		private dialog: MatDialog
	) { }

  	ngOnInit(): void {
		this.loadUsers();
  	}

	private loadUsers() {
		this.server.getUsers().subscribe({
			next: (v: any) => {
				/*v.forEach((user: any) => {
					user.databaseSizeStr = this.utils.printFilesize(user.databaseSize);
				});*/
				this.dataSource.data = v;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	public createUser() {
		const dialog = this.dialog.open(CreateUserDialogComponent);
		dialog.afterClosed().subscribe(newUsername => {
			if(newUsername) {
				this.loadUsers();
			}
		});
	}
}
