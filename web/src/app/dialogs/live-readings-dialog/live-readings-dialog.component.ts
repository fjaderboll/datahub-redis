import { Component, OnInit, OnDestroy, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { RouterLink } from '@angular/router';
import { DecimalPipe } from '@angular/common';
import { Subscription } from 'rxjs';
import { LiveReadingsService } from '../../services/live-readings.service';
import { UtilsService } from '../../services/utils.service';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatChipSet, MatChip, MatChipAvatar, MatChipRemove } from '@angular/material/chips';
import { Reading } from '../../models';

/** Only readings of this dataset, node or sensor are shown */
export interface LiveReadingsData {
	datasetName?: string;
	nodeName?: string;
	sensorName?: string;
}

const MAX_READINGS = 10;

@Component({
	selector: 'app-live-readings-dialog',
	templateUrl: './live-readings-dialog.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./live-readings-dialog.component.scss'],
	imports: [MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose, MatButton, MatIcon, MatChipSet, MatChip, MatChipAvatar, MatChipRemove, RouterLink, DecimalPipe]
})
export class LiveReadingsDialogComponent implements OnInit, OnDestroy {
	dialogRef = inject<MatDialogRef<LiveReadingsDialogComponent>>(MatDialogRef);
	private liveReadings = inject(LiveReadingsService);
	utils = inject(UtilsService);
	public filter = { ...inject<LiveReadingsData>(MAT_DIALOG_DATA) };

	private startTime = 0;
	private streamSubscription?: Subscription;
	public receivedReadings = 0;
	public receivedReadingsPerSecond: number = 0.0;
	public lastReadings: Reading[] = [];
	public streamingReadings = false;

	public static open(dialog: MatDialog, data: LiveReadingsData) {
		return dialog.open(LiveReadingsDialogComponent, {
			data,
			width: '1000px',
			maxWidth: 'calc(100vw - 16px)'
		});
	}

	ngOnInit(): void {
		this.streamReadings();
	}

	ngOnDestroy(): void {
		this.streamSubscription?.unsubscribe(); // closes the connection, unless the dashboard listens too
	}

	public streamReadings() {
		this.streamingReadings = true;
		this.resetReadings();

		this.streamSubscription = this.liveReadings.readings$.subscribe({
			next: (reading) => {
				this.handleReading(reading);
			},
			error: () => {
				this.streamingReadings = false; // the service has told the user
			},
			complete: () => {
				this.streamingReadings = false;
			}
		});
	}

	public getFilterTitle() {
		return [this.filter.datasetName, this.filter.nodeName, this.filter.sensorName].filter(name => name).join(' → ');
	}

	public clearFilter() {
		this.filter = {};
		this.resetReadings();
	}

	private resetReadings() {
		this.startTime = Date.now();
		this.receivedReadings = 0;
		this.receivedReadingsPerSecond = 0;
		this.lastReadings = [];
	}

	private matchesFilter(reading: Reading) {
		return (!this.filter.datasetName || reading.datasetName == this.filter.datasetName)
			&& (!this.filter.nodeName || reading.nodeName == this.filter.nodeName)
			&& (!this.filter.sensorName || reading.sensorName == this.filter.sensorName);
	}

	private handleReading(reading: Reading) {
		if(!this.matchesFilter(reading)) {
			return;
		}

		this.receivedReadings++;
		this.receivedReadingsPerSecond = this.receivedReadings / ((Date.now() - this.startTime) / 1000);

		this.lastReadings.unshift(reading);
		if(this.lastReadings.length > MAX_READINGS) {
			this.lastReadings.pop();
		}
	}

}
