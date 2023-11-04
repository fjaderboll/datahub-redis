import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateDatasetDialogComponent } from './create-dataset-dialog.component';

describe('CreateDatasetDialogComponent', () => {
  let component: CreateDatasetDialogComponent;
  let fixture: ComponentFixture<CreateDatasetDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CreateDatasetDialogComponent]
    });
    fixture = TestBed.createComponent(CreateDatasetDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
