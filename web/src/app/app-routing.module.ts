import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { authGuardGuard } from './guards/auth-guard.guard';
import { UserViewComponent } from './pages/user-view/user-view.component';
import { UserListComponent } from './pages/user-list/user-list.component';
import { DatasetListComponent } from './pages/dataset-list/dataset-list.component';
import { DatasetViewComponent } from './pages/dataset-view/dataset-view.component';
import { NodeViewComponent } from './pages/node-view/node-view.component';
import { TokenListComponent } from './pages/token-list/token-list.component';
import { ExportListComponent } from './pages/export-list/export-list.component';
import { SensorViewComponent } from './pages/sensor-view/sensor-view.component';
import { TimeserieListComponent } from './pages/timeserie-list/timeserie-list.component';
import { SettingsViewComponent } from './pages/settings-view/settings-view.component';

const routes: Routes = [
    { path: 'login', component: LoginComponent },
    { path: 'datasets', component: DatasetListComponent, canActivate: [authGuardGuard] },
    { path: 'datasets/:datasetName', component: DatasetViewComponent, canActivate: [authGuardGuard] },
    { path: 'datasets/:datasetName/nodes/:nodeName', component: NodeViewComponent, canActivate: [authGuardGuard] },
    { path: 'datasets/:datasetName/nodes/:nodeName/sensors/:sensorName', component: SensorViewComponent, canActivate: [authGuardGuard] },
    { path: 'tokens', component: TokenListComponent, canActivate: [authGuardGuard] },
    { path: 'exports', component: ExportListComponent, canActivate: [authGuardGuard] },
    { path: 'users', component: UserListComponent, canActivate: [authGuardGuard] },
    { path: 'users/:username', component: UserViewComponent, canActivate: [authGuardGuard] },
	{ path: 'timeseries', component: TimeserieListComponent, canActivate: [authGuardGuard] },
	{ path: 'settings', component: SettingsViewComponent, canActivate: [authGuardGuard] },
    { path: '', component: DashboardComponent, canActivate: [authGuardGuard] },
    { path: '**', redirectTo: '', canActivate: [authGuardGuard] }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
