import { Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';

@Component({
  selector: 'app-inline-edit',
  templateUrl: './inline-edit.component.html',
  styleUrls: ['./inline-edit.component.scss']
})
export class InlineEditComponent implements OnInit {
	@Input() type: string = "text";
	@Input() disabled: boolean = false;
	@Input() value: any;
	@Output() onChange: EventEmitter<number> = new EventEmitter<number>();
	@ViewChild('input') inputElement!: ElementRef;
	public editMode: boolean = false;
	public newValue: any;

	constructor() { }

	ngOnInit(): void {
	}

	startEdit() {
		if(!this.disabled) {
			this.editMode = true;
			this.newValue = this.value;
			setTimeout(() => {
				if(this.inputElement) {
					this.inputElement.nativeElement.focus();
				}
			}, 100);
		}
	}

	stopEdit(save: boolean) {
		if(save && this.value != this.newValue) {
			this.onChange.emit(this.newValue);
		}
		this.editMode = false;
	}
}
