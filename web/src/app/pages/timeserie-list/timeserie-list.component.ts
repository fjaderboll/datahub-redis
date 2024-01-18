import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { Observable } from 'rxjs';
import { ConfirmDialogComponent } from 'src/app/dialogs/confirm-dialog/confirm-dialog.component';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-timeserie-list',
	templateUrl: './timeserie-list.component.html',
	styleUrls: ['./timeserie-list.component.scss']
})
export class TimeserieListComponent implements OnInit, AfterViewInit {
	public displayedColumns: string[] = ['datasetName', 'nodeName', 'sensorName', 'samples', 'memory', 'retention'];
	public dataSource = new MatTableDataSource<any>();

	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	public totalTimeseries = 0;
	public totalSamples = 0;
	public totalMemory = 0;
	public system: any;
	public settings: any;
	private datasets: any;

	constructor(
		private server: ServerService,
		public utils: UtilsService,
		private dialog: MatDialog
	) { }

	ngOnInit(): void {
		this.loadSystem();
		this.loadSettings();
		this.loadDatasets();
  	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadSystem() {
		this.server.getStateSystem().subscribe({
			next: (system: any) => {
				this.system = system;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private loadSettings() {
		this.server.getStateSettings().subscribe({
			next: (settings: any) => {
				this.settings = settings;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private loadDatasets() {
		this.server.getDatasets().subscribe({
			next: (datasets: any) => {
				this.datasets = datasets;
				this.loadTimeseries();
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private loadTimeseries() {
		this.server.getStateTimeseries().subscribe({
			next: (timeseries: any) => {
				this.dataSource.data = timeseries;

				this.totalTimeseries = timeseries.length;
				this.totalSamples = 0;
				this.totalMemory = 0;
				timeseries.forEach((ts: any) => {
					this.totalSamples += ts.samples;
					this.totalMemory += ts.memory;
				});
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public hasAccess(timeserie: any) {
		return this.datasets.some((dataset: any) => {
			return dataset.name === timeserie.datasetName;
		});
	}

	public updateSetting(setting: string, newValue: any) {
		this.server.updateStateSettings(setting, newValue).subscribe({
			next: (response: any) => {
				this.loadSettings();
				this.utils.toastSuccess(response);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public applyRetention() {
		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Apply retention",
				text: "This will update the rentetion on all existing timeseries to " + this.utils.getDeltaTime(this.settings.retention*1000) + ". Are you sure?",
				action: new Observable(
					observer => {
						this.server.updateStateSettings('applyRetention', true).subscribe({
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
				this.loadTimeseries();
			}
		});
	}

}

