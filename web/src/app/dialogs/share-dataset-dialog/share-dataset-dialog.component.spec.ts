import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ShareDatasetDialogComponent } from './share-dataset-dialog.component';

describe('ShareDatasetDialogComponent', () => {
  let component: ShareDatasetDialogComponent;
  let fixture: ComponentFixture<ShareDatasetDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ShareDatasetDialogComponent]
    });
    fixture = TestBed.createComponent(ShareDatasetDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
