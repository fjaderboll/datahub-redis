import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SettingsViewComponent } from './settings-view.component';

describe('SettingsViewComponent', () => {
  let component: SettingsViewComponent;
  let fixture: ComponentFixture<SettingsViewComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SettingsViewComponent]
    });
    fixture = TestBed.createComponent(SettingsViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
