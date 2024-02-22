import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { ConfirmDialogComponent } from 'src/app/dialogs/confirm-dialog/confirm-dialog.component';
import { CreateNodeDialogComponent } from 'src/app/dialogs/create-node-dialog/create-node-dialog.component';
import { ShareDatasetDialogComponent } from 'src/app/dialogs/share-dataset-dialog/share-dataset-dialog.component';
import { VisualizeReadingsDialogComponent } from 'src/app/dialogs/visualize-readings-dialog/visualize-readings-dialog.component';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
  selector: 'app-dataset-view',
  templateUrl: './dataset-view.component.html',
  styleUrls: ['./dataset-view.component.scss']
})
export class DatasetViewComponent implements OnInit, AfterViewInit {
	public datasetName!: string;
	public dataset: any;
	public datasetUsers!: string[];

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
		this.datasetName = this.route.snapshot.paramMap.get('datasetName') || 'this should never happen';

		this.loadDataset();
		this.loadDatasetUsers();
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadDataset() {
		this.server.getDataset(this.datasetName).subscribe({
			next: (dataset: any) => {
				this.dataset = dataset;
				this.dataSource.data = dataset.nodes;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private loadDatasetUsers() {
		this.server.getDatasetUsers(this.datasetName).subscribe({
			next: (datasetUsers: any) => {
				this.datasetUsers = datasetUsers;
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

	public visualizeReadings() {
		this.dialog.open(VisualizeReadingsDialogComponent, {
			data: {
				datasetName: this.datasetName
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

	public shareDataset() {
		const dialog = this.dialog.open(ShareDatasetDialogComponent, {
			data: {
				datasetName: this.dataset.name
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
				action: new Observable(
					observer => {
						this.server.unshareDataset(this.dataset.name, username).subscribe({
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
				if(self) {
					this.router.navigate(['/datasets']);
				} else {
					this.loadDatasetUsers();
				}
			}
		});
	}

}
