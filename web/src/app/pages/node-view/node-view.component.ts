import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { ConfirmDialogComponent } from 'src/app/dialogs/confirm-dialog/confirm-dialog.component';
import { CreateNodeDialogComponent } from 'src/app/dialogs/create-node-dialog/create-node-dialog.component';
import { CreateSensorDialogComponent } from 'src/app/dialogs/create-sensor-dialog/create-sensor-dialog.component';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-node-view',
	templateUrl: './node-view.component.html',
	styleUrls: ['./node-view.component.scss']
})
export class NodeViewComponent  implements OnInit, AfterViewInit {
	public datasetName!: string;
	public node: any;

	public displayedColumns: string[] = ['name', 'desc'];
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
		this.loadNode();
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadNode() {
		this.datasetName = this.route.snapshot.paramMap.get('datasetName') || 'this should never happen';
		let nodeName = this.route.snapshot.paramMap.get('nodeName') || 'this should never happen';

		this.server.getNode(this.datasetName, nodeName).subscribe({
			next: (node: any) => {
				this.node = node;
				this.dataSource.data = node.sensors;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public changedValue(property: string, newValue: any) {
		this.server.updateNode(this.datasetName, this.node.name, property, newValue).subscribe({
			next: (response: any) => {
				this.node[property] = newValue;
				if(property == "name") {
					this.router.navigate(['/datasets/' + this.datasetName + '/nodes/' + this.node.name]);
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
				action: new Observable(
					observer => {
						this.server.deleteNode(this.datasetName, this.node.name).subscribe({
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
				this.router.navigate(['/datasets/' + this.datasetName]);
			}
		});
	}

	public createSensor() {
		const dialog = this.dialog.open(CreateSensorDialogComponent, {
			data: {
				datasetName: this.datasetName,
                nodeName: this.node.name
			}
		});
		dialog.afterClosed().subscribe(sensor => {
			if(sensor) {
				this.loadNode();
			}
		});
	}

}
