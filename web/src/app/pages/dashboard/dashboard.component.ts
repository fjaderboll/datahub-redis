import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { Chart } from 'angular-highcharts';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-dashboard',
	templateUrl: './dashboard.component.html',
	styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, AfterViewInit {
	public displayedColumns: string[] = ['datasetName', 'nodeName', 'sensorName', 'samples', 'memory', 'retention'];
	public dataSource = new MatTableDataSource<any>();

	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	public memoryChart!: Chart;

	constructor(
		public auth: AuthenticationService,
		private server: ServerService,
		public utils: UtilsService
	) { }

	ngOnInit(): void {
		if(this.auth.isAdmin()) {
			this.loadSystem();
			this.loadTimeseries();
		}
  	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadSystem() {
		this.server.getStateSystem().subscribe({
			next: (system: any) => {
				this.createMemoryChart(system);
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
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private createMemoryChart(system: any) {
		const mem =  system.memory;
		const utils = this.utils;

		this.memoryChart = new Chart({
			chart: {
				plotBackgroundColor: undefined,
				plotBorderWidth: 0,
				plotShadow: false
			},
			title: {
				text: 'Memory<br/>' + system.memory.percent + '%',
				align: 'center',
				verticalAlign: 'middle',
				y: 60
			},
			tooltip: {
				pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
			},
			accessibility: {
				point: {
					valueSuffix: '%'
				}
			},
			credits: {
				enabled: false
			},
			plotOptions: {
				pie: {
					showInLegend: true,
					dataLabels: {
						enabled: true,
						distance: -50,
						style: {
							fontWeight: 'bold',
							color: 'white'
						}
					},
					startAngle: -90,
					endAngle: 90,
					center: ['50%', '75%'],
					size: '110%',
					colors: [
						'#bfbfbf',
						'#db802a',
						'#498bfc',
						'#63c970'
					]
				}
			},
			legend: {
				enabled: true,
				labelFormatter: function() {
					const thiz = this as any;
					return this.name + ' ' + utils.printFilesize(thiz.y);
				},
				floating: true,
				y: -60
			},
			series: [
				{
					type: 'pie',
					name: 'Memory usage',
					innerSize: '50%',
					data: [
						['Other', mem.total - mem.application - mem.database - mem.available],
						['Application', mem.application],
						['Database', mem.database],
						['Available', mem.available]
					]
				}
			]
		});
	}

}
