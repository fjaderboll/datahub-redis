import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { ConfirmDialogComponent } from 'src/app/dialogs/confirm-dialog/confirm-dialog.component';
import { CreateNodeDialogComponent } from 'src/app/dialogs/create-node-dialog/create-node-dialog.component';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-dataset-view',
  templateUrl: './dataset-view.component.html',
  styleUrls: ['./dataset-view.component.scss']
})
export class DatasetViewComponent implements OnInit, AfterViewInit {
	public dataset: any;

	public displayedColumns: string[] = ['name', 'desc'];
	public dataSource = new MatTableDataSource<any>();
	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	constructor(
		public auth: AuthenticationService,
		public utils: UtilsService,
		private server: ServerService,
		private route: ActivatedRoute,
		private dialog: MatDialog,
		private router: Router
	) { }

	ngOnInit(): void {
		this.loadDataset();
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadDataset() {
		let datasetName = this.route.snapshot.paramMap.get('datasetName') || 'this should never happen';

		this.server.getDataset(datasetName).subscribe({
			next: (dataset: any) => {
				this.dataset = dataset;
				this.dataSource.data = dataset.nodes;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public changedValue(property: string, newValue: any) {
		this.server.updateDataset(this.dataset.name, property, newValue).subscribe({
			next: (response: any) => {
				this.dataset[property] = newValue;
				if(property == "name") {
					this.router.navigate(['/datasets/' + this.dataset.name]);
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
				action: new Observable(
					observer => {
						this.server.deleteDataset(this.dataset.name).subscribe({
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
				this.router.navigate(['/datasets']);
			}
		});
	}

	public createNode() {
		const dialog = this.dialog.open(CreateNodeDialogComponent, {
			data: {
				datasetName: this.dataset.name
			}
		});
		dialog.afterClosed().subscribe(node => {
			if(node) {
				this.loadDataset();
			}
		});
	}

}
