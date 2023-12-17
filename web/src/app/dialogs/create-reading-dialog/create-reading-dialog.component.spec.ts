import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateReadingDialogComponent } from './create-reading-dialog.component';

describe('CreateReadingDialogComponent', () => {
  let component: CreateReadingDialogComponent;
  let fixture: ComponentFixture<CreateReadingDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CreateReadingDialogComponent]
    });
    fixture = TestBed.createComponent(CreateReadingDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
