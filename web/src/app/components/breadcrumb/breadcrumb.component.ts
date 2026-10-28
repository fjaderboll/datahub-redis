import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { RouterLink } from '@angular/router';

@Component({
	selector: 'app-breadcrumb',
	templateUrl: './breadcrumb.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./breadcrumb.component.scss'],
	imports: [MatIcon, RouterLink]
})
export class BreadcrumbComponent {
	@Input() links!: string[];
	@Input() names!: (string | null | undefined)[];
}
