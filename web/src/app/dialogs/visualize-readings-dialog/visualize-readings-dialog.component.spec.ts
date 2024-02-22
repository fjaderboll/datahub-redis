import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VisualizeReadingsDialogComponent } from './visualize-readings-dialog.component';

describe('VisualizeReadingsDialogComponent', () => {
  let component: VisualizeReadingsDialogComponent;
  let fixture: ComponentFixture<VisualizeReadingsDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [VisualizeReadingsDialogComponent]
    });
    fixture = TestBed.createComponent(VisualizeReadingsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
