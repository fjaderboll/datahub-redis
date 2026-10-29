import { Component, DestroyRef, OnInit, ChangeDetectionStrategy, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval } from 'rxjs';
import { RouterLink } from '@angular/router';
import { DecimalPipe } from '@angular/common';
import { AuthenticationService } from '../../services/authentication.service';
import { LiveReadingsService } from '../../services/live-readings.service';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { SystemMemoryComponent } from '../../components/system-memory/system-memory.component';
import { MatIcon } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { NodeActivity, Overview, Reading } from '../../models';

const RECENT_NODES = 10;
const DAY = 24 * 3600 * 1000;

@Component({
	selector: 'app-dashboard',
	templateUrl: './dashboard.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./dashboard.component.scss'],
	imports: [SystemMemoryComponent, RouterLink, DecimalPipe, MatIcon, MatTooltip]
})
export class DashboardComponent implements OnInit {
	auth = inject(AuthenticationService);
	private server = inject(ServerService);
	private liveReadings = inject(LiveReadingsService);
	private destroyRef = inject(DestroyRef);
	utils = inject(UtilsService);

	public overview?: Overview;
	public readingsSinceLoad = 0;
	public sinceLoadLabel = '';
	private loadTime = 0;

	ngOnInit(): void {
		this.server.getStateOverview().subscribe({
			next: (overview) => {
				this.overview = overview;
				this.listenForReadings();
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public trackNode(node: NodeActivity) {
		return node.datasetName + '/' + node.nodeName;
	}

	/** Keeps the recently updated nodes up to date, the silent ones are only checked on load */
	private listenForReadings() {
		this.loadTime = Date.now();
		this.updateSinceLoadLabel();
		interval(1000).pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => this.updateSinceLoadLabel());

		this.liveReadings.readings$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
			next: (reading) => {
				this.handleReading(reading);
			},
			error: () => {} // the service has told the user
		});
	}

	private updateSinceLoadLabel() {
		const seconds = Math.floor((Date.now() - this.loadTime) / 1000);
		if(seconds < 60) {
			this.sinceLoadLabel = seconds + ' s';
		} else if(seconds < 3600) {
			this.sinceLoadLabel = Math.floor(seconds / 60) + ' min';
		} else {
			this.sinceLoadLabel = Math.floor(seconds / 3600) + ' h';
		}
	}

	private handleReading(reading: Reading) {
		const overview = this.overview!;
		this.readingsSinceLoad++;
		const time = new Date(reading.timestamp).getTime();
		if(Date.now() - time < DAY) {
			overview.readings24h++;
		}

		let node = overview.recentNodes.find(n => n.datasetName == reading.datasetName && n.nodeName == reading.nodeName);
		if(!node) {
			node = { datasetName: reading.datasetName, nodeName: reading.nodeName, lastTimestamp: reading.timestamp, sensors: [] };
			overview.recentNodes.push(node);
		}

		let sensor = node.sensors.find(s => s.name == reading.sensorName);
		if(!sensor) {
			sensor = { name: reading.sensorName, unit: reading.unit, lastReading: null, interval: null, silent: false };
			node.sensors.push(sensor);
		}

		// older readings, e.g. from an import, don't replace newer ones
		if(!sensor.lastReading || time >= new Date(sensor.lastReading.timestamp).getTime()) {
			sensor.lastReading = reading;
		}
		if(time > new Date(node.lastTimestamp).getTime()) {
			node.lastTimestamp = reading.timestamp;
		}

		overview.recentNodes = overview.recentNodes
			.sort((n1, n2) => new Date(n2.lastTimestamp).getTime() - new Date(n1.lastTimestamp).getTime())
			.slice(0, RECENT_NODES);
	}

}
