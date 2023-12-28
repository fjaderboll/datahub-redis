import { Component, OnInit } from '@angular/core';
import { Chart } from 'angular-highcharts';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-dashboard',
	templateUrl: './dashboard.component.html',
	styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
	public memoryChart!: Chart;

	constructor(
		public auth: AuthenticationService,
		private server: ServerService,
		public utils: UtilsService
	) { }

	ngOnInit(): void {
		if(this.auth.isAdmin()) {
			this.loadSystem();
		}
		//this.chart.addPoint(Math.floor(Math.random() * 10));
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

	private createMemoryChart(system: any) {
		const mem =  system.memory;
		const multiplier = 1 / 1024 / 1024;

		this.memoryChart = new Chart({
			chart: {
				type: 'pie',
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
					size: '110%'
				}
			},
			legend: {
				enabled: true,
				labelFormat: '{name} {y:.0f} MB',
				floating: true,
				y: -60
			},
			series: [
				{
					type: 'pie',
					name: 'Memory usage',
					innerSize: '50%',
					data: [
						['Other', (mem.total - mem.application - mem.database - mem.available) * multiplier],
						['Application', mem.application * multiplier],
						['Database', mem.database * multiplier],
						['Available', mem.available * multiplier]
					]
				}
			]
		});
	}

}
