import { Component } from '@angular/core';
import { MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from '@angular/platform-browser';

@Component({
	selector: 'app-root',
	templateUrl: './app.component.html',
	styleUrls: ['./app.component.scss']
})
export class AppComponent {
	constructor(
        private matIconRegistry: MatIconRegistry,
        private domSanitizer: DomSanitizer
    ){
		this.matIconRegistry.addSvgIcon('datahub', this.domSanitizer.bypassSecurityTrustResourceUrl('../assets/img/logo/logo-white.min.svg'));
		this.matIconRegistry.addSvgIcon('swagger', this.domSanitizer.bypassSecurityTrustResourceUrl('../assets/img/icons/swagger-black-white.min.svg'));
		this.matIconRegistry.addSvgIcon('loading', this.domSanitizer.bypassSecurityTrustResourceUrl('../assets/img/icons/loading.svg'));
	}
}
