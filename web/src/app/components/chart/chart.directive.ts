import { Directive, ElementRef, Input, NgZone, OnChanges, OnDestroy, inject } from '@angular/core';
import Highcharts from 'highcharts/esm/highcharts';
import 'highcharts/esm/modules/accessibility';

/**
 * Renders a Highcharts chart in the host element, recreated whenever new options are given.
 * Usage: <div [appChart]="options"></div>
 */
@Directive({
	selector: '[appChart]'
})
export class ChartDirective implements OnChanges, OnDestroy {
	private element = inject(ElementRef);
	private zone = inject(NgZone);
	private chart?: Highcharts.Chart;

	@Input() appChart?: Highcharts.Options;

	ngOnChanges() {
		this.chart?.destroy();
		this.chart = undefined;
		if(this.appChart) {
			// mouse tracking would otherwise run change detection on every mouse move
			this.chart = this.zone.runOutsideAngular(() => Highcharts.chart(this.element.nativeElement, this.appChart!));
		}
	}

	ngOnDestroy() {
		this.chart?.destroy();
	}
}
