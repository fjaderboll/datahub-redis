import { AfterViewInit, Component, OnInit, ViewChild, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { CreateDatasetDialogComponent } from '../../dialogs/create-dataset-dialog/create-dataset-dialog.component';
import { VisualizeReadingsDialogComponent } from '../../dialogs/visualize-readings-dialog/visualize-readings-dialog.component';
import { ServerService } from '../../services/server.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { Dataset } from '../../models';

@Component({
	selector: 'app-dataset-list',
	templateUrl: './dataset-list.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./dataset-list.component.scss'],
	imports: [BreadcrumbComponent, MatButton, MatIcon, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, RouterLink, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator]
})
export class DatasetListComponent implements OnInit, AfterViewInit {
	private server = inject(ServerService);
	private dialog = inject(MatDialog);

	public displayedColumns: string[] = ['name', 'nodeCount', 'desc'];
	public dataSource = new MatTableDataSource<Dataset>();

	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	ngOnInit(): void {
		this.loadDatasets();
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadDatasets() {
		this.server.getDatasets().subscribe({
			next: (datasets) => {
				this.dataSource.data = datasets;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public visualizeReadings() {
		VisualizeReadingsDialogComponent.open(this.dialog, {});
	}

	public createDataset() {
		const dialog = this.dialog.open(CreateDatasetDialogComponent);
		dialog.afterClosed().subscribe(dataset => {
			if(dataset) {
				this.loadDatasets();
			}
		});
	}

}
