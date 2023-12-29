import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
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
	private datasets: any;

	constructor(
		private server: ServerService,
		public utils: UtilsService
	) { }

	ngOnInit(): void {
		this.loadSystem();
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

	public changedValue(property: string, newValue: any) {
		this.server.updateStateSystem(property, newValue).subscribe({
			next: (response: any) => {
				this.loadSystem();
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

}

