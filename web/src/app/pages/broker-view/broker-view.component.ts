import { AfterViewInit, Component, DestroyRef, OnInit, ViewChild, ChangeDetectionStrategy, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval } from 'rxjs';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { RouterLink } from '@angular/router';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { BrokerClient, BrokerState } from '../../models';

const BROKER_REFRESH = 5000; // milliseconds

@Component({
	selector: 'app-broker-view',
	templateUrl: './broker-view.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./broker-view.component.scss'],
	imports: [BreadcrumbComponent, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatSortHeader, MatCellDef, MatCell, RouterLink, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator]
})
export class BrokerViewComponent implements OnInit, AfterViewInit {
	private server = inject(ServerService);
	private destroyRef = inject(DestroyRef);
	utils = inject(UtilsService);

	public displayedColumns: string[] = ['clientId', 'username', 'address', 'connectedAt', 'protocolVersion', 'subscriptions'];
	public dataSource = new MatTableDataSource<BrokerClient>();

	@ViewChild(MatPaginator) paginator!: MatPaginator;
	@ViewChild(MatSort) sort!: MatSort;

	public broker?: BrokerState;
	public refreshFailed = false;

	constructor() {
		this.dataSource.sortingDataAccessor = (client, column) => {
			switch(column) {
				case 'subscriptions': return client.subscriptions.length;
				default: return (client as any)[column] ?? '';
			}
		};
	}

	ngOnInit(): void {
		this.loadBroker();
		interval(BROKER_REFRESH).pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => this.loadBroker());
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
	}

	private loadBroker() {
		this.server.getStateBroker().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
			next: (broker) => {
				this.broker = broker;
				this.dataSource.data = broker.clients;
				this.refreshFailed = false;
			},
			error: (e) => {
				if(this.broker) { // shown on the page rather than a toast every refresh
					this.refreshFailed = true;
				} else {
					this.server.showHttpError(e);
				}
			}
		});
	}

	/** The topic's levels, each but the last ending with its slash */
	public topicLevels(topic: string) {
		return topic.split(/(?<=\/)/);
	}

}
