import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateTokenDialogComponent } from './create-token-dialog.component';

describe('CreateTokenDialogComponent', () => {
  let component: CreateTokenDialogComponent;
  let fixture: ComponentFixture<CreateTokenDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CreateTokenDialogComponent]
    });
    fixture = TestBed.createComponent(CreateTokenDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
