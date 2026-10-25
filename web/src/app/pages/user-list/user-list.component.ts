import { AfterViewInit, Component, OnInit, ViewChild, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { CreateUserDialogComponent } from '../../dialogs/create-user-dialog/create-user-dialog.component';
import { ServerService } from '../../services/server.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { User } from '../../models';

@Component({
	selector: 'app-user-list',
	templateUrl: './user-list.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./user-list.component.scss'],
	imports: [BreadcrumbComponent, MatButton, MatIcon, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, RouterLink, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator]
})
export class UserListComponent implements OnInit, AfterViewInit {
	private server = inject(ServerService);
	private dialog = inject(MatDialog);

	public displayedColumns: string[] = ['username', 'email', 'isAdmin'];
	public dataSource = new MatTableDataSource<User>();

	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	ngOnInit(): void {
		this.loadUsers();
	}

	private loadUsers() {
		this.server.getUsers().subscribe({
			next: (users) => {
				this.dataSource.data = users;
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
