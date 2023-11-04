import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExportListComponent } from './export-list.component';

describe('ExportListComponent', () => {
  let component: ExportListComponent;
  let fixture: ComponentFixture<ExportListComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ExportListComponent]
    });
    fixture = TestBed.createComponent(ExportListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
