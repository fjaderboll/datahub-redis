import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { ConfirmDialogComponent } from 'src/app/dialogs/confirm-dialog/confirm-dialog.component';
import { CreateReadingDialogComponent } from 'src/app/dialogs/create-reading-dialog/create-reading-dialog.component';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-sensor-view',
	templateUrl: './sensor-view.component.html',
	styleUrls: ['./sensor-view.component.scss']
})
export class SensorViewComponent implements OnInit, AfterViewInit {
	public datasetName!: string;
	public nodeName: any;
	public sensorName: any;
	public sensor: any;
	public readings: any;
	private readingsLimit = 1000;

	public displayedColumns: string[] = ['timestamp', 'value'];
	public dataSource = new MatTableDataSource<any>();
	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	constructor(
		public auth: AuthenticationService,
		public utils: UtilsService,
		private server: ServerService,
		private route: ActivatedRoute,
		private dialog: MatDialog,
		private router: Router
	) { }

	ngOnInit(): void {
		this.datasetName = this.route.snapshot.paramMap.get('datasetName') || 'this should never happen';
		this.nodeName = this.route.snapshot.paramMap.get('nodeName') || 'this should never happen';
		this.sensorName = this.route.snapshot.paramMap.get('sensorName') || 'this should never happen';

		this.loadSensor();
		this.loadReadings();
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadSensor() {
		this.server.getSensor(this.datasetName, this.nodeName, this.sensorName).subscribe({
			next: (sensor: any) => {
				this.sensor = sensor;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private loadReadings() {
		this.server.getReadings(this.datasetName, this.nodeName, this.sensorName, this.readingsLimit).subscribe({
			next: (readings: any) => {
				this.readings = readings;
				this.dataSource.data = readings;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public loadMore() {
		this.readingsLimit *= 2;
		this.loadReadings();
	}

	public changedValue(property: string, newValue: any) {
		this.server.updateSensor(this.datasetName, this.nodeName, this.sensorName, property, newValue).subscribe({
			next: (response: any) => {
				this.sensor[property] = newValue;
				if(property == "name") {
					this.router.navigate(['/datasets/' + this.datasetName + '/nodes/' + this.nodeName + '/sensors/' + this.sensor.name]);
				}
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public deleteSensor() {
		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Delete Sensor",
				text: "This will remove this sensor and all its readings. Are you sure?",
				action: new Observable(
					observer => {
						this.server.deleteSensor(this.datasetName, this.nodeName, this.sensorName).subscribe({
							next: (v: any) => {
								observer.next(v);
							},
							error: (e) => {
								observer.error(e);
							},
							complete: () => {
								observer.complete();
							}
						});
					}
				)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				this.router.navigate(['/datasets/' + this.datasetName + '/nodes/' + this.nodeName]);
			}
		});
	}

	public createReading() {
		const dialog = this.dialog.open(CreateReadingDialogComponent, {
			data: {
				datasetName: this.datasetName,
                nodeName: this.nodeName,
				sensorName: this.sensorName
			}
		});
		dialog.afterClosed().subscribe(sensor => {
			if(sensor) {
				this.loadSensor();
				this.loadReadings();
			}
		});
	}

	public deleteReadings() {
		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Delete Readings",
				text: "This will remove all readings for this sensor. Are you sure?",
				action: new Observable(
					observer => {
						this.server.deleteReadings(this.datasetName, this.nodeName, this.sensorName).subscribe({
							next: (v: any) => {
								observer.next(v);
							},
							error: (e) => {
								observer.error(e);
							},
							complete: () => {
								observer.complete();
							}
						});
					}
				)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				this.loadSensor();
				this.loadReadings();
			}
		});
	}

}
