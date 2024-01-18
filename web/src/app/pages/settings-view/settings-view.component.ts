import { Component } from '@angular/core';
import { ServerService } from 'src/app/services/server.service';
import { UtilsService } from 'src/app/services/utils.service';

@Component({
	selector: 'app-settings-view',
	templateUrl: './settings-view.component.html',
	styleUrls: ['./settings-view.component.scss']
})
export class SettingsViewComponent {
	public settings: any;

	constructor(
		private server: ServerService,
		public utils: UtilsService
	) { }

	ngOnInit(): void {
		this.loadSettings();
  	}

	private loadSettings() {
		this.server.getStateSettings().subscribe({
			next: (settings: any) => {
				this.settings = settings;
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}

	public updateSetting(setting: string, newValue: any) {
		this.server.updateStateSettings(setting, newValue).subscribe({
			next: (response: any) => {
				this.loadSettings();
				this.utils.toastSuccess(response);
			},
			error: (e) => {
				this.server.showHttpError(e);
			}
		});
	}
}
