import { AfterViewInit, Component, DestroyRef, OnInit, ViewChild, ChangeDetectionStrategy, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { ActivatedRoute, Router } from '@angular/router';
import { ConfirmDialogComponent } from '../../dialogs/confirm-dialog/confirm-dialog.component';
import { CreateReadingDialogComponent } from '../../dialogs/create-reading-dialog/create-reading-dialog.component';
import { VisualizeReadingsDialogComponent } from '../../dialogs/visualize-readings-dialog/visualize-readings-dialog.component';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { InlineEditComponent } from '../../components/inline-edit/inline-edit.component';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { Reading, Sensor } from '../../models';

@Component({
	selector: 'app-sensor-view',
	templateUrl: './sensor-view.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./sensor-view.component.scss'],
	imports: [BreadcrumbComponent, InlineEditComponent, MatButton, MatIcon, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator]
})
export class SensorViewComponent implements OnInit, AfterViewInit {
	utils = inject(UtilsService);
	private server = inject(ServerService);
	private route = inject(ActivatedRoute);
	private dialog = inject(MatDialog);
	private router = inject(Router);
	private destroyRef = inject(DestroyRef);

	public datasetName!: string;
	public nodeName!: string;
	public sensorName!: string;
	public sensor?: Sensor;
	public readings?: Reading[];
	private readingsLimit = 1000;

	public displayedColumns: string[] = ['timestamp', 'value'];
	public dataSource = new MatTableDataSource<Reading>();
	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	ngOnInit(): void {
		// the component is reused when only the URL changes, e.g. after a rename
		this.route.paramMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(params => {
			this.datasetName = params.get('datasetName')!;
			this.nodeName = params.get('nodeName')!;
			this.sensorName = params.get('sensorName')!;
			this.loadSensor();
			this.loadReadings();
		});
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadSensor() {
		this.server.getSensor(this.datasetName, this.nodeName, this.sensorName).subscribe({
			next: (sensor) => {
				this.sensor = sensor;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private loadReadings() {
		this.server.getSensorReadings(this.datasetName, this.nodeName, this.sensorName, this.readingsLimit, null).subscribe({
			next: (readings) => {
				this.readings = readings;
				this.dataSource.data = readings;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public hasMoreReadings() {
		return !!this.readings && !!this.sensor?.readingStats && this.readings.length < this.sensor.readingStats.count;
	}

	public loadMore() {
		this.readingsLimit *= 2;
		this.loadReadings();
	}

	public changedValue(property: 'name' | 'desc' | 'unit', newValue: string) {
		this.server.updateSensor(this.datasetName, this.nodeName, this.sensorName, property, newValue).subscribe({
			next: () => {
				this.sensor![property] = newValue;
				if(property == "name") {
					this.router.navigate(['/datasets', this.datasetName, 'nodes', this.nodeName, 'sensors', newValue], { replaceUrl: true });
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
				action: this.server.deleteSensor(this.datasetName, this.nodeName, this.sensorName)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				this.router.navigate(['/datasets', this.datasetName, 'nodes', this.nodeName]);
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
		dialog.afterClosed().subscribe(reading => {
			if(reading) {
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
				action: this.server.deleteReadings(this.datasetName, this.nodeName, this.sensorName)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				this.loadSensor();
				this.loadReadings();
			}
		});
	}

	public visualizeReadings() {
		VisualizeReadingsDialogComponent.open(this.dialog, {
			datasetName: this.datasetName,
			nodeName: this.nodeName,
			sensorName: this.sensorName,
			readings: this.readings
		});
	}

}
