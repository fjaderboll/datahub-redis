import { Component, OnInit, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import type Highcharts from 'highcharts/esm/highcharts';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { ChartDirective } from '../../components/chart/chart.directive';
import { Reading } from '../../models';

export interface VisualizeReadingsData {
	datasetName?: string;
	nodeName?: string;
	sensorName?: string;
	/** Already loaded readings, newest first */
	readings?: Reading[];
}

@Component({
	selector: 'app-visualize-readings-dialog',
	templateUrl: './visualize-readings-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./visualize-readings-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, ChartDirective, MatDialogActions, MatButton, MatDialogClose, MatIcon]
})
export class VisualizeReadingsDialogComponent implements OnInit {
	dialogRef = inject<MatDialogRef<VisualizeReadingsDialogComponent>>(MatDialogRef);
	private server = inject(ServerService);
	utils = inject(UtilsService);
	data = inject<VisualizeReadingsData>(MAT_DIALOG_DATA);

	public after: number = -3*3600;
	private readings: Reading[] = [];
	public readingsChart?: Highcharts.Options;
	public loading: boolean = false;

	public static open(dialog: MatDialog, data: VisualizeReadingsData) {
		return dialog.open(VisualizeReadingsDialogComponent, {
			data,
			width: '1000px',
			maxWidth: 'calc(100vw - 16px)'
		});
	}

	ngOnInit(): void {
		if(this.data.readings) {
			this.readings = this.data.readings;
			this.updateRange(this.readings);
			this.createReadingsChart();
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
		return names.join(' → ');
	}

	private getSerieName(reading: Reading) {
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

	private createReadingsChart() {
		let yAxis: Highcharts.YAxisOptions[] = [];
		let series: { type: 'line', name: string, yAxis: number, tooltip: Highcharts.SeriesTooltipOptionsObject, data: [number, number][] }[] = [];
		this.readings.forEach((reading) => {
			let serie = series.find((s) => {
				return s.name == this.getSerieName(reading);
			});
			if(!serie) {
				let i = yAxis.findIndex((ya) => {
					return ya.title?.text == reading.unit;
				});
				if(i < 0) {
					yAxis.push({
						title: {
							text: reading.unit
						},
						opposite: yAxis.length % 2 == 1
					});
					i = yAxis.length - 1;
				}

				serie = {
					type: 'line',
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

		series.forEach((serie) => {
			serie.data.sort((r1, r2) => {
				return r1[0] - r2[0];
			});
		});

		this.readingsChart = {
			chart: {
				zooming: {
					type: 'x'
				}
			},
			title: {
				text: this.readings.length + ' readings in the last ' + this.utils.getDeltaTime(-this.after*1000)
			},
			credits: {
				enabled: false
			},
			xAxis: {
				type: 'datetime'
			},
			yAxis: yAxis,
			time: {
				timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
			},
			series: series
		};
	}

	private loadReadings() {
		this.loading = true;
		const observer = {
			next: (readings: Reading[]) => {
				this.readings = readings;
				this.createReadingsChart();
				this.loading = false;
			},
			error: (e: any) => {
				this.server.showHttpError(e);
				this.loading = false;
			}
		};

		const limit = 0; // all within the time range
		const after = this.after + '';
		if(this.data.sensorName) {
			this.server.getSensorReadings(this.data.datasetName!, this.data.nodeName!, this.data.sensorName, limit, after).subscribe(observer);
		} else if(this.data.nodeName) {
			this.server.getNodeReadings(this.data.datasetName!, this.data.nodeName, limit, after).subscribe(observer);
		} else if(this.data.datasetName) {
			this.server.getDatasetReadings(this.data.datasetName, limit, after).subscribe(observer);
		} else {
			this.server.getReadings(limit, after).subscribe(observer);
		}
	}

	public loadMore() {
		this.updateRange(null);
		this.loadReadings();
	}

	private updateRange(readings: Reading[] | null) {
		this.after *= 2;

		// readings given by the caller: start from the oldest of them
		if(readings) {
			const n = readings.length;
			if(n > 0) {
				const oldestReading = readings[n - 1];
				const age = Date.now() - new Date(oldestReading.timestamp).getTime();
				this.after = -Math.max(Math.round(age/1000), 1);
			}
		}
	}

}
