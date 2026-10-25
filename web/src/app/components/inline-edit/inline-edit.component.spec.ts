import { ComponentFixture, TestBed } from '@angular/core/testing';
import { InlineEditComponent } from './inline-edit.component';

describe('InlineEditComponent', () => {
	let fixture: ComponentFixture<InlineEditComponent>;
	let emitted: any[];

	function create(type: string, value: any) {
		fixture = TestBed.createComponent(InlineEditComponent);
		fixture.componentRef.setInput('type', type);
		fixture.componentRef.setInput('value', value);
		emitted = [];
		fixture.componentInstance.onChange.subscribe(v => emitted.push(v));
		fixture.detectChanges();
	}

	function edit(text: string) {
		fixture.nativeElement.querySelector('.view').click();
		fixture.detectChanges();
		const input: HTMLInputElement = document.querySelector('.edit input')!;
		input.value = text;
		input.dispatchEvent(new Event('input'));
		return input;
	}

	const key = (key: string) => new KeyboardEvent('keydown', { key, bubbles: true });
	const focusOut = () => new FocusEvent('focusout', { bubbles: true });

	it('saves once on Enter, although removing the input also fires focusout', () => {
		create('text', 'old');
		const input = edit('new');
		input.dispatchEvent(key('Enter'));
		input.dispatchEvent(focusOut());
		expect(emitted).toEqual(['new']);
	});

	it('does not save on Escape', () => {
		create('text', 'old');
		const input = edit('new');
		input.dispatchEvent(key('Escape'));
		input.dispatchEvent(focusOut());
		expect(emitted).toEqual([]);
	});

	it('saves when leaving the field', () => {
		create('text', 'old');
		edit('new').dispatchEvent(focusOut());
		expect(emitted).toEqual(['new']);
	});

	it('does not save an unchanged value', () => {
		create('text', 'old');
		edit('old').dispatchEvent(key('Enter'));
		expect(emitted).toEqual([]);
	});

	it('emits numbers for number fields', () => {
		create('number', 60);
		edit('3600').dispatchEvent(key('Enter'));
		expect(emitted).toEqual([3600]);
	});

	it('can not be edited when disabled', () => {
		create('text', 'old');
		fixture.componentRef.setInput('disabled', true);
		fixture.detectChanges();
		fixture.nativeElement.querySelector('.view').click();
		fixture.detectChanges();
		expect(document.querySelector('.edit')).toBeNull();
	});
});
