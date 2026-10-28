import { Component, ElementRef, EventEmitter, Injector, Input, NgZone, Output, ViewChild, ChangeDetectionStrategy, afterNextRender, inject } from '@angular/core';
import { MatFormField, MatHint } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatRadioGroup, MatRadioButton } from '@angular/material/radio';
import { CdkConnectedOverlay, CdkOverlayOrigin, ConnectedOverlayPositionChange, ConnectedPosition } from '@angular/cdk/overlay';
import { MatAutocomplete, MatAutocompleteTrigger, MatOption } from '@angular/material/autocomplete';

@Component({
	selector: 'app-inline-edit',
	templateUrl: './inline-edit.component.html',
	changeDetection: ChangeDetectionStrategy.Eager,
	styleUrls: ['./inline-edit.component.scss'],
	imports: [MatFormField, MatHint, MatInput, FormsModule, MatRadioGroup, MatRadioButton, CdkConnectedOverlay, CdkOverlayOrigin, MatAutocomplete, MatAutocompleteTrigger, MatOption]
})
export class InlineEditComponent {
	private injector = inject(Injector);
	private zone = inject(NgZone);

	// the popup is an overlay, so tables that scroll sideways don't cut it off
	public readonly positions: ConnectedPosition[] = [
		{ originX: 'start', originY: 'bottom', overlayX: 'start', overlayY: 'top', offsetY: 10 },
		{ originX: 'end', originY: 'bottom', overlayX: 'end', overlayY: 'top', offsetY: 10 }
	];
	public alignEnd = false;

	@Input() type: 'text' | 'number' | 'boolean' = "text";
	@Input() disabled: boolean = false;
	@Input() value: any;
	@Input() placeholder: string = "";
	/** What to edit, when it differs from the displayed value */
	@Input() editValue: any;
	@Input() hint: string = "";
	/** Suggestions for a text, which can still be anything */
	@Input() options: string[] = [];
	@Output() onChange = new EventEmitter<any>();
	@ViewChild('edit') editElement?: ElementRef<HTMLElement>;
	@ViewChild(MatAutocompleteTrigger) autocompleteTrigger?: MatAutocompleteTrigger;
	public editMode: boolean = false;
	public newValue: any;
	private startValue: any;

	startEdit() {
		if(!this.disabled && !this.editMode) {
			this.editMode = true;
			this.startValue = (this.editValue !== undefined ? this.editValue : this.value);
			this.newValue = this.startValue;
			afterNextRender(() => {
				this.editElement?.nativeElement.querySelector('input')?.focus();
			}, { injector: this.injector });
		}
	}

	stopEdit(save: boolean) {
		// removing the focused input fires focusout too, which must not save a second time
		if(!this.editMode) {
			return;
		}
		this.editMode = false;
		if(save && this.startValue != this.newValue) {
			const v = (this.type == 'number' ? Number(this.newValue) : this.newValue);
			this.onChange.emit(v);
		}
	}

	// the arrow follows the side the popup is aligned to
	positionChange(change: ConnectedOverlayPositionChange) {
		this.zone.run(() => this.alignEnd = (change.connectionPair.overlayX == 'end'));
	}

	setBoolean(value: boolean) {
		this.newValue = value;
		this.stopEdit(true);
	}

	// all options until something is typed, then those containing it
	getOptions() {
		if(this.newValue == this.startValue) {
			return this.options;
		}
		const text = String(this.newValue ?? '').toLowerCase();
		return this.options.filter(option => option.toLowerCase().includes(text));
	}

	selectOption(value: string) {
		this.newValue = value;
		this.stopEdit(true);
	}

	// an option picked with the arrow keys is saved by selectOption instead
	enterPressed() {
		if(!this.autocompleteTrigger?.activeOption) {
			this.stopEdit(true);
		}
	}

	// leaving the popup saves text, but cancels a boolean choice not yet made
	focusOut(event: FocusEvent) {
		if(!this.editElement?.nativeElement.contains(event.relatedTarget as Node | null)) {
			this.stopEdit(this.type != 'boolean');
		}
	}
}
