import { Component, OnInit } from '@angular/core';
import { Chart } from 'angular-highcharts';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-system-memory',
	templateUrl: './system-memory.component.html',
	styleUrls: ['./system-memory.component.scss']
})
export class SystemMemoryComponent implements OnInit {
	public memoryChart!: Chart;

	constructor(
		private server: ServerService,
		public utils: UtilsService
	) { }

	ngOnInit(): void {
		this.loadSystem();
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
				y: -20
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
					//center: ['50%', '75%'],
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
				y: -150
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
