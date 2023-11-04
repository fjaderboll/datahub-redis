import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DatasetViewComponent } from './dataset-view.component';

describe('DatasetViewComponent', () => {
  let component: DatasetViewComponent;
  let fixture: ComponentFixture<DatasetViewComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DatasetViewComponent]
    });
    fixture = TestBed.createComponent(DatasetViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
