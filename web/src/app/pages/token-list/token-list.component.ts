import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { Observable } from 'rxjs';
import { ConfirmDialogComponent } from 'src/app/dialogs/confirm-dialog/confirm-dialog.component';
import { CreateTokenDialogComponent } from 'src/app/dialogs/create-token-dialog/create-token-dialog.component';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-token-list',
  templateUrl: './token-list.component.html',
  styleUrls: ['./token-list.component.scss']
})
export class TokenListComponent implements OnInit, AfterViewInit {
	public displayedColumns: string[] = ['desc', 'enabled', 'token', 'expire', 'actions'];
	public dataSource = new MatTableDataSource<any>();

	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

  	constructor(
		public auth: AuthenticationService,
		private server: ServerService,
		public utils: UtilsService,
		private dialog: MatDialog
	) { }

  	ngOnInit(): void {
		this.loadTokens();
  	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadTokens() {
		this.server.getTokens().subscribe({
			next: (tokens: any) => {
				this.dataSource.data = tokens;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public changedValue(token: any, property: string, newValue: any) {
		this.server.updateToken(token.id, property, newValue).subscribe({
			next: (response: any) => {
				token[property] = newValue;
                this.loadTokens();
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public createToken() {
		const dialog = this.dialog.open(CreateTokenDialogComponent);
		dialog.afterClosed().subscribe(token => {
			if(token) {
				this.loadTokens();
			}
		});
	}

	public deleteToken(token: any) {
		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Delete Token",
				text: "All devices using this token to will no longer function. Proceed?",
				action: new Observable(
					observer => {
						this.server.deleteToken(token.id).subscribe({
							next: (v: any) => {
								observer.next(v);
							},
							error: (e) => {
								observer.error(e);
							},
							complete: () => {
								observer.complete();
							}
						});
					}
				)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				this.loadTokens();
			}
		});
	}

}
