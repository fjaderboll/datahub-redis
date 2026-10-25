import { AfterViewInit, Component, OnInit, ViewChild, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { ConfirmDialogComponent } from '../../dialogs/confirm-dialog/confirm-dialog.component';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { SystemMemoryComponent } from '../../components/system-memory/system-memory.component';
import { InlineEditComponent } from '../../components/inline-edit/inline-edit.component';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { Settings, Timeserie } from '../../models';

@Component({
	selector: 'app-timeserie-list',
	templateUrl: './timeserie-list.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./timeserie-list.component.scss'],
	imports: [BreadcrumbComponent, SystemMemoryComponent, InlineEditComponent, MatButton, MatIcon, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, RouterLink, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator]
})
export class TimeserieListComponent implements OnInit, AfterViewInit {
	private server = inject(ServerService);
	utils = inject(UtilsService);
	private dialog = inject(MatDialog);

	public displayedColumns: string[] = ['datasetName', 'nodeName', 'sensorName', 'samples', 'memory', 'retention'];
	public dataSource = new MatTableDataSource<Timeserie>();

	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	public totalTimeseries = 0;
	public totalSamples = 0;
	public totalMemory = 0;
	public settings?: Settings;
	private accessibleDatasets = new Set<string>();

	ngOnInit(): void {
		this.loadSettings();
		this.loadDatasets();
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadSettings() {
		this.server.getStateSettings().subscribe({
			next: (settings) => {
				this.settings = settings;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private loadDatasets() {
		this.server.getDatasets().subscribe({
			next: (datasets) => {
				this.accessibleDatasets = new Set(datasets.map(dataset => dataset.name));
				this.loadTimeseries();
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	private loadTimeseries() {
		this.server.getStateTimeseries().subscribe({
			next: (timeseries) => {
				this.dataSource.data = timeseries;

				this.totalTimeseries = timeseries.length;
				this.totalSamples = 0;
				this.totalMemory = 0;
				timeseries.forEach((ts) => {
					this.totalSamples += ts.samples;
					this.totalMemory += ts.memory;
				});
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	// administrators see all timeseries, but can only open the datasets they have access to
	public hasAccess(timeserie: Timeserie) {
		return this.accessibleDatasets.has(timeserie.datasetName);
	}

	public updateSetting(setting: string, newValue: any) {
		this.server.updateStateSettings(setting, newValue).subscribe({
			next: (message) => {
				this.loadSettings();
				this.utils.toastSuccess(message);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public applyRetention() {
		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Apply retention",
				text: "This will update the retention on all existing timeseries to " + this.utils.printDuration(this.settings?.retention, 'forever') + ". Are you sure?",
				action: this.server.updateStateSettings('applyRetention', true)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				this.loadTimeseries();
			}
		});
	}

}
