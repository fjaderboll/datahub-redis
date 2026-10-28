import { AfterViewInit, Component, DestroyRef, OnInit, ViewChild, ChangeDetectionStrategy, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ConfirmDialogComponent } from '../../dialogs/confirm-dialog/confirm-dialog.component';
import { CreateSensorDialogComponent } from '../../dialogs/create-sensor-dialog/create-sensor-dialog.component';
import { VisualizeReadingsDialogComponent } from '../../dialogs/visualize-readings-dialog/visualize-readings-dialog.component';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { InlineEditComponent } from '../../components/inline-edit/inline-edit.component';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { DatasetNode, Sensor } from '../../models';

@Component({
	selector: 'app-node-view',
	templateUrl: './node-view.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./node-view.component.scss'],
	imports: [BreadcrumbComponent, InlineEditComponent, MatButton, MatIcon, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, RouterLink, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator]
})
export class NodeViewComponent implements OnInit, AfterViewInit {
	utils = inject(UtilsService);
	private server = inject(ServerService);
	private route = inject(ActivatedRoute);
	private dialog = inject(MatDialog);
	private router = inject(Router);
	private destroyRef = inject(DestroyRef);

	public datasetName!: string;
	public nodeName!: string;
	public node?: DatasetNode;

	public displayedColumns: string[] = ['name', 'lastReading', 'desc'];
	public dataSource = new MatTableDataSource<Sensor>();
	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	constructor() {
		// sort on time of the last reading, not the reading object
		this.dataSource.sortingDataAccessor = (sensor, column) => {
			if(column == 'lastReading') {
				return sensor.lastReading?.timestamp ?? '';
			}
			return (sensor as any)[column];
		};
	}

	ngOnInit(): void {
		// the component is reused when only the URL changes, e.g. after a rename
		this.route.paramMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(params => {
			this.datasetName = params.get('datasetName')!;
			this.nodeName = params.get('nodeName')!;
			this.loadNode();
		});
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadNode() {
		this.server.getNode(this.datasetName, this.nodeName).subscribe({
			next: (node) => {
				this.node = node;
				this.dataSource.data = node.sensors ?? [];
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public changedValue(property: 'name' | 'desc', newValue: string) {
		this.server.updateNode(this.datasetName, this.nodeName, property, newValue).subscribe({
			next: () => {
				this.node![property] = newValue;
				if(property == "name") {
					this.router.navigate(['/datasets', this.datasetName, 'nodes', newValue], { replaceUrl: true });
				}
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public deleteNode() {
		const dialog = this.dialog.open(ConfirmDialogComponent, {
			data: {
				title: "Delete Node",
				text: "This will remove this node and all its sensors and readings. Are you sure?",
				action: this.server.deleteNode(this.datasetName, this.nodeName)
			}
		});
		dialog.afterClosed().subscribe(confirmed => {
			if(confirmed) {
				this.router.navigate(['/datasets', this.datasetName]);
			}
		});
	}

	public createSensor() {
		const dialog = this.dialog.open(CreateSensorDialogComponent, {
			data: {
				datasetName: this.datasetName,
				nodeName: this.nodeName
			}
		});
		dialog.afterClosed().subscribe(sensor => {
			if(sensor) {
				this.loadNode();
			}
		});
	}

	public visualizeReadings() {
		VisualizeReadingsDialogComponent.open(this.dialog, {
			datasetName: this.datasetName,
			nodeName: this.nodeName
		});
	}

}
