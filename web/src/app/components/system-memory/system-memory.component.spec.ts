import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SystemMemoryComponent } from './system-memory.component';

describe('SystemMemoryComponent', () => {
  let component: SystemMemoryComponent;
  let fixture: ComponentFixture<SystemMemoryComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SystemMemoryComponent]
    });
    fixture = TestBed.createComponent(SystemMemoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
