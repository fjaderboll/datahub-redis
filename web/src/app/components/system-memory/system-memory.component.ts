import { Component, OnInit, ChangeDetectionStrategy, inject } from '@angular/core';
import type Highcharts from 'highcharts/esm/highcharts';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { ChartDirective } from '../chart/chart.directive';
import { SystemState } from '../../models';

@Component({
	selector: 'app-system-memory',
	templateUrl: './system-memory.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./system-memory.component.scss'],
	imports: [ChartDirective]
})
export class SystemMemoryComponent implements OnInit {
	private server = inject(ServerService);
	utils = inject(UtilsService);

	public memoryChart?: Highcharts.Options;

	ngOnInit(): void {
		this.loadSystem();
	}

	private loadSystem() {
		this.server.getStateSystem().subscribe({
			next: (system) => {
				this.createMemoryChart(system);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private createMemoryChart(system: SystemState) {
		const mem = system.memory;
		const utils = this.utils;
		const other = Math.max(0, mem.total - mem.application - mem.database - mem.available);

		this.memoryChart = {
			chart: {
				height: 260,
				plotBackgroundColor: undefined,
				plotBorderWidth: 0,
				plotShadow: false,
				spacing: [0, 0, 10, 0]
			},
			title: {
				text: 'Memory<br/>' + mem.percent + '%',
				align: 'center',
				verticalAlign: 'middle',
				y: 40
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
						distance: -40,
						style: {
							fontWeight: 'bold',
							color: 'white'
						}
					},
					startAngle: -90,
					endAngle: 90,
					center: ['50%', '85%'],
					size: '160%',
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
				}
			},
			series: [
				{
					type: 'pie',
					name: 'Memory usage',
					innerSize: '50%',
					data: [
						['Other', other],
						['Application', mem.application],
						['Database', mem.database],
						['Available', mem.available]
					]
				}
			],
			responsive: {
				rules: [{
					// slice labels don't fit on small screens, the legend has the same information
					condition: { maxWidth: 500 },
					chartOptions: {
						plotOptions: { pie: { dataLabels: { enabled: false } } }
					}
				}]
			}
		};
	}

}
