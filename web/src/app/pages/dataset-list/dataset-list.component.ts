import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { CreateDatasetDialogComponent } from 'src/app/dialogs/create-dataset-dialog/create-dataset-dialog.component';
import { VisualizeReadingsDialogComponent } from 'src/app/dialogs/visualize-readings-dialog/visualize-readings-dialog.component';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-dataset-list',
  templateUrl: './dataset-list.component.html',
  styleUrls: ['./dataset-list.component.scss']
})
export class DatasetListComponent implements OnInit, AfterViewInit {
	public displayedColumns: string[] = ['name', 'desc'];
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
		this.loadDatasets();
  	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadDatasets() {
		this.server.getDatasets().subscribe({
			next: (v: any) => {
				/*this.totalReadingCount = 0;
				v.forEach((node: any) => {
					this.totalReadingCount += node.readingCount;
					node.lastReadingTimestamp = node.lastReading?.timestamp;
				});*/
				this.dataSource.data = v;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public visualizeReadings() {
		this.dialog.open(VisualizeReadingsDialogComponent, {
			data: {}
		});
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
