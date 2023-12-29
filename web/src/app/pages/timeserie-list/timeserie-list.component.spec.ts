import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TimeserieListComponent } from './timeserie-list.component';

describe('TimeserieListComponent', () => {
  let component: TimeserieListComponent;
  let fixture: ComponentFixture<TimeserieListComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TimeserieListComponent]
    });
    fixture = TestBed.createComponent(TimeserieListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
