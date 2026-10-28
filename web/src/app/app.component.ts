import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from '@angular/platform-browser';
import { HeaderComponent } from './components/header/header.component';
import { RouterOutlet } from '@angular/router';
import { FooterComponent } from './components/footer/footer.component';
import { LiveReadingsButtonComponent } from './components/live-readings-button/live-readings-button.component';

@Component({
	selector: 'app-root',
	templateUrl: './app.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./app.component.scss'],
	imports: [HeaderComponent, RouterOutlet, FooterComponent, LiveReadingsButtonComponent]
})
export class AppComponent {
	constructor() {
		const matIconRegistry = inject(MatIconRegistry);
		const domSanitizer = inject(DomSanitizer);

		matIconRegistry.addSvgIcon('datahub', domSanitizer.bypassSecurityTrustResourceUrl('assets/img/logo/logo-white.min.svg'));
		matIconRegistry.addSvgIcon('swagger', domSanitizer.bypassSecurityTrustResourceUrl('assets/img/icons/swagger-black-white.min.svg'));
		matIconRegistry.addSvgIcon('loading', domSanitizer.bypassSecurityTrustResourceUrl('assets/img/icons/loading.svg'));
	}
}
