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

	public totalSamples = 0;
	public totalMemory = 0;
	public system: any;

	constructor(
		private server: ServerService,
		public utils: UtilsService
	) { }

	ngOnInit(): void {
		this.loadSystem();
		this.loadTimeseries();
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

	private loadTimeseries() {
		this.server.getStateTimeseries().subscribe({
			next: (timeseries: any) => {
				this.dataSource.data = timeseries;

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

