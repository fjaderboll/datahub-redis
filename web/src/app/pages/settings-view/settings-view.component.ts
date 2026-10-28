import { Component, OnInit, ChangeDetectionStrategy, inject } from '@angular/core';
import { ServerService } from '../../services/server.service';
import { UtilsService } from '../../services/utils.service';
import { BreadcrumbComponent } from '../../components/breadcrumb/breadcrumb.component';
import { InlineEditComponent } from '../../components/inline-edit/inline-edit.component';
import { Settings } from '../../models';

@Component({
	selector: 'app-settings-view',
	templateUrl: './settings-view.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./settings-view.component.scss'],
	imports: [BreadcrumbComponent, InlineEditComponent]
})
export class SettingsViewComponent implements OnInit {
	private server = inject(ServerService);
	utils = inject(UtilsService);

	public settings?: Settings;

	ngOnInit(): void {
		this.loadSettings();
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
}
