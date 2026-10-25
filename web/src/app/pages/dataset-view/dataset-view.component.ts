import { AfterViewInit, Component, DestroyRef, OnInit, ViewChild, ChangeDetectionStrategy, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ConfirmDialogComponent } from '../../dialogs/confirm-dialog/confirm-dialog.component';
import { CreateNodeDialogComponent } from '../../dialogs/create-node-dialog/create-node-dialog.component';
import { ShareDatasetDialogComponent } from '../../dialogs/share-dataset-dialog/share-dataset-dialog.component';
import { VisualizeReadingsDialogComponent } from '../../dialogs/visualize-readings-dialog/visualize-readings-dialog.component';
import { AuthenticationService } from '../../services/authentication.service';
import { ServerService } from '../../services/server.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { InlineEditComponent } from '../../components/inline-edit/inline-edit.component';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatChipSet, MatChip, MatChipRemove } from '@angular/material/chips';
import { Dataset, DatasetNode } from '../../models';

@Component({
	selector: 'app-dataset-view',
	templateUrl: './dataset-view.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./dataset-view.component.scss'],
	imports: [BreadcrumbComponent, InlineEditComponent, RouterLink, MatButton, MatIcon, MatChipSet, MatChip, MatChipRemove, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator]
})
export class DatasetViewComponent implements OnInit, AfterViewInit {
	auth = inject(AuthenticationService);
	private server = inject(ServerService);
	private route = inject(ActivatedRoute);
	private dialog = inject(MatDialog);
	private router = inject(Router);
	private destroyRef = inject(DestroyRef);

	public datasetName!: string;
	public dataset?: Dataset;
	public datasetUsers: string[] = [];

	public displayedColumns: string[] = ['name', 'desc'];
	public dataSource = new MatTableDataSource<DatasetNode>();
	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	ngOnInit(): void {
		// the component is reused when only the URL changes, e.g. after a rename
		this.route.paramMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(params => {
			this.datasetName = params.get('datasetName')!;
			this.loadDataset();
			this.loadDatasetUsers();
		});
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadDataset() {
		this.server.getDataset(this.datasetName).subscribe({
			next: (dataset) => {
				this.dataset = dataset;
				this.dataSource.data = dataset.nodes ?? [];
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private loadDatasetUsers() {
		this.server.getDatasetUsers(this.datasetName).subscribe({
			next: (datasetUsers) => {
				this.datasetUsers = datasetUsers;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public changedValue(property: 'name' | 'desc', newValue: string) {
		this.server.updateDataset(this.datasetName, property, newValue).subscribe({
			next: () => {
				this.dataset![property] = newValue;
				if(property == "name") {
					this.router.navigate(['/datasets', newValue], { replaceUrl: true });
				}
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public deleteDataset() {
		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Delete Dataset",
				text: "This will remove this dataset and all its nodes, sensors and readings. Are you sure?",
				action: this.server.deleteDataset(this.datasetName)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				this.router.navigate(['/datasets']);
			}
		});
	}

	public visualizeReadings() {
		VisualizeReadingsDialogComponent.open(this.dialog, {
			datasetName: this.datasetName
		});
	}

	public createNode() {
		const dialog = this.dialog.open(CreateNodeDialogComponent, {
			data: {
				datasetName: this.datasetName
			}
		});
		dialog.afterClosed().subscribe(node => {
			if(node) {
				this.loadDataset();
			}
		});
	}

	public shareDataset() {
		const dialog = this.dialog.open(ShareDatasetDialogComponent, {
			data: {
				datasetName: this.datasetName
			}
		});
		dialog.afterClosed().subscribe(username => {
			if(username) {
				this.loadDatasetUsers();
			}
		});
	}

	public unshareDataset(username: string) {
		const self = this.auth.getUsername() === username;
		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Unshare Dataset",
				text: "This will remove access to this dataset for user '" + username + "'"+(self ? " (yourself!)" : "")+". Are you sure?",
				action: this.server.unshareDataset(this.datasetName, username)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				if(self) {
					this.router.navigate(['/datasets']);
				} else {
					this.loadDatasetUsers();
				}
			}
		});
	}

}
