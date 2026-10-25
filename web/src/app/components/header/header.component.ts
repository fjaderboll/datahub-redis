import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { AuthenticationService } from '../../services/authentication.service';
import { environment } from '../../../environments/environment';
import { MatToolbar } from '@angular/material/toolbar';
import { MatAnchor, MatButton, MatIconButton } from '@angular/material/button';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { MatIcon } from '@angular/material/icon';
import { MatMenuTrigger, MatMenu, MatMenuItem } from '@angular/material/menu';
import { MatDivider } from '@angular/material/divider';

@Component({
	selector: 'app-header',
	templateUrl: './header.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./header.component.scss'],
	imports: [MatToolbar, MatAnchor, MatButton, MatIconButton, RouterLink, RouterLinkActive, MatIcon, MatMenuTrigger, MatMenu, MatMenuItem, MatDivider]
})
export class HeaderComponent {
	public auth = inject(AuthenticationService);
	public apiUrl = environment.apiUrl;
	public docUrl = 'https://github.com/fjaderboll/datahub-redis';

	public logout() {
		this.auth.logout();
	}

}
