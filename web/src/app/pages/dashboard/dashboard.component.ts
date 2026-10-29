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

const DAY = 24 * 3600 * 1000;
const OVERVIEW_REFRESH = 60 * 1000;

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
		this.loadOverview();
		interval(OVERVIEW_REFRESH).pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => this.loadOverview());
	}

	/** The node lists are only refreshed now and then, so they stay put long enough to be clicked */
	private loadOverview() {
		this.server.getStateOverview().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
			next: (overview) => {
				const first = !this.overview;
				this.overview = overview;
				if(first) {
					this.listenForReadings();
				}
			},
			error: (e) => {
				if(!this.overview) { // stale lists are better than a toast every minute
					this.server.showHttpError(e);
				}
			}
		});
	}

	public trackNode(node: NodeActivity) {
		return node.datasetName + '/' + node.nodeName;
	}

	/** Keeps the reading counts up to date between the overview refreshes */
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
		this.readingsSinceLoad++;
		if(Date.now() - new Date(reading.timestamp).getTime() < DAY) {
			this.overview!.readings24h++;
		}
	}

}
