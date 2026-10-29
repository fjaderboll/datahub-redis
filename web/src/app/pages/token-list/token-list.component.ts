import { AfterViewInit, Component, OnInit, ViewChild, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { CdkCopyToClipboard } from '@angular/cdk/clipboard';
import { ConfirmDialogComponent } from '../../dialogs/confirm-dialog/confirm-dialog.component';
import { CreateTokenDialogComponent } from '../../dialogs/create-token-dialog/create-token-dialog.component';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { InlineEditComponent } from '../../components/inline-edit/inline-edit.component';
import { Token } from '../../models';

@Component({
	selector: 'app-token-list',
	templateUrl: './token-list.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./token-list.component.scss'],
	imports: [BreadcrumbComponent, MatButton, MatIconButton, MatIcon, CdkCopyToClipboard, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, InlineEditComponent, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator]
})
export class TokenListComponent implements OnInit, AfterViewInit {
	private server = inject(ServerService);
	utils = inject(UtilsService);
	private dialog = inject(MatDialog);

	public displayedColumns: string[] = ['desc', 'enabled', 'mqttOnly', 'token', 'expire', 'actions'];
	public dataSource = new MatTableDataSource<Token>();

	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	// the full token is only returned when created, so it is shown until dismissed or the page is left
	public createdToken: Token | null = null;

	constructor() {
		this.dataSource.sortingDataAccessor = (token, column) => {
			switch(column) {
				case 'id': return Number(token.id); // creation order
				case 'expire': return token.expire ?? '9999'; // never expiring last
				default: return (token as any)[column] ?? '';
			}
		};
	}

	ngOnInit(): void {
		this.loadTokens();
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadTokens() {
		this.server.getTokens().subscribe({
			next: (tokens) => {
				this.dataSource.data = tokens;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	/** Seconds left, as the time-to-live to edit */
	public getTTL(token: Token) {
		if(token.expire) {
			return Math.max(0, Math.round((new Date(token.expire).getTime() - Date.now()) / 1000));
		}
		return '';
	}

	public changedValue(token: Token, property: string, newValue: any) {
		this.server.updateToken(token.id, property, newValue).subscribe({
			next: () => {
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
				this.createdToken = token;
				this.loadTokens();
			}
		});
	}

	public copied() {
		this.utils.toastSuccess("Token copied to clipboard");
	}

	public deleteToken(token: Token) {
		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Revoke Token",
				text: "All devices using this token will no longer function. Proceed?",
				action: this.server.deleteToken(token.id)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				this.loadTokens();
			}
		});
	}

}
