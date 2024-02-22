import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';
import { Chart } from 'angular-highcharts';

@Component({
	selector: 'app-visualize-readings-dialog',
	templateUrl: './visualize-readings-dialog.component.html',
	styleUrls: ['./visualize-readings-dialog.component.scss']
})
export class VisualizeReadingsDialogComponent  implements OnInit {
	private inputData: any;
	public readingsLimit = 1000;
	public readingsChart!: Chart;

	constructor(
		public dialogRef: MatDialogRef<VisualizeReadingsDialogComponent>,
		private server: ServerService,
		private utils: UtilsService,
        @Inject(MAT_DIALOG_DATA) public data: any
	) {}

	ngOnInit(): void {
		if(this.data.readings) {
			this.readingsLimit = this.data.readings.length;
			console.log(this.readingsLimit);
			this.createMemoryChart();
		} else {
			this.loadReadings();
		}
	}

	public getTitle() {
		let names = [];
		if(this.data.datasetName) {
			names.push(this.data.datasetName);
		}
		if(this.data.nodeName) {
			names.push(this.data.nodeName);
		}
		if(this.data.sensorName) {
			names.push(this.data.sensorName);
		}

		if(names.length == 0) {
			names.push('all datasets');
		}
		return names.join(' &rarr; ');
	}

	private getSerieName(reading: any) {
		const divider = ' - ';
		if(this.data.sensorName) {
			return reading.sensorName;
		} else if(this.data.nodeName) {
			return reading.sensorName;
		} else if(this.data.datasetName) {
			return reading.nodeName + divider + reading.sensorName;
		} else {
			return reading.datasetName + divider + reading.nodeName + divider + reading.sensorName;
		}
	}

	private createMemoryChart() {
		let yAxis: any = [];
		let series: any = [];
		this.data.readings.forEach((reading: any) => {
			let serie: any = series.find((s: any) => {
				return s.name == this.getSerieName(reading);
			});
			if(!serie) {
				let i: any = yAxis.findIndex((ya: any) => {
					return ya.title.text == reading.unit;
				});
				if(i < 0) {
					yAxis.push({
						title: {
							text: reading.unit
						}
					});
					i = yAxis.length - 1;
				}

				serie = {
					name: this.getSerieName(reading),
					yAxis: i,
					tooltip: {
						valueSuffix: ' ' + reading.unit
					},
					data: []
				};
				series.push(serie);
			}

			let t = new Date(reading.timestamp).getTime();
			serie.data.push([t, reading.value]);
		});

		series.forEach((serie: any) => {
			serie.data.sort((r1: any, r2: any) => {
				return r1[0] - r2[0];
			});
		});

		this.readingsChart = new Chart({
			chart: {
				type: 'line',
				zooming: {
					type: 'x'
				}
			},
			title: {
				text: (this.data.sensorName || this.data.nodeName || this.data.datasetName || 'all readings') + ' - ' + this.data.readings.length + ' readings'
			},
			xAxis: {
                type: 'datetime'
            },
			yAxis: yAxis,
            time: {
				useUTC: false
			},
			series: series
		});
	}

	private loadReadings() {
		const observer = {
			next: (readings: any) => {
				this.data.readings = readings;
				this.createMemoryChart();
				console.log(this.readingsLimit);
				console.log(this.data.readings.length);
			},
			error: (e: any) => {
				this.server.showHttpError(e);
			}
		};

		if(this.data.sensorName) {
			this.server.getSensorReadings(this.data.datasetName, this.data.nodeName, this.data.sensorName, this.readingsLimit).subscribe(observer);
		} else if(this.data.nodeName) {
			this.server.getNodeReadings(this.data.datasetName, this.data.nodeName, this.readingsLimit).subscribe(observer);
		} else if(this.data.datasetName) {
			this.server.getDatasetReadings(this.data.datasetName, this.readingsLimit).subscribe(observer);
		} else {
			this.server.getReadings(this.readingsLimit).subscribe(observer);
		}
	}

	public loadMore() {
		if(this.readingsLimit % 1000 != 0) {
			this.readingsLimit = (Math.floor(this.data.readings.length / 1000) + 1) * 1000;
		}
		this.readingsLimit *= 2;
		this.loadReadings();
	}

}
