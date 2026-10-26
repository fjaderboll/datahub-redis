import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatFabButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { AuthenticationService } from '../../services/authentication.service';
import { LiveReadingsData, LiveReadingsDialogComponent } from '../../dialogs/live-readings-dialog/live-readings-dialog.component';

@Component({
	selector: 'app-live-readings-button',
	templateUrl: './live-readings-button.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./live-readings-button.component.scss'],
	imports: [MatFabButton, MatIcon, MatTooltip]
})
export class LiveReadingsButtonComponent {
	auth = inject(AuthenticationService);
	private router = inject(Router);
	private dialog = inject(MatDialog);

	public openLiveReadings() {
		LiveReadingsDialogComponent.open(this.dialog, this.getViewedEntity());
	}

	/** The dataset, node or sensor of the page being viewed, taken from the route so the pages don't have to tell */
	private getViewedEntity(): LiveReadingsData {
		let route = this.router.routerState.snapshot.root;
		while(route.firstChild) {
			route = route.firstChild;
		}
		return {
			datasetName: route.params['datasetName'],
			nodeName: route.params['nodeName'],
			sensorName: route.params['sensorName']
		};
	}

}
