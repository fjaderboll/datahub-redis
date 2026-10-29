import { Routes } from '@angular/router';
import { adminGuard, authGuard } from './guards/auth.guard';

// pages are loaded on demand, which keeps Highcharts out of the initial bundle
export const routes: Routes = [
	{ path: 'login', loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent) },
	{ path: 'datasets', canActivate: [authGuard], loadComponent: () => import('./pages/dataset-list/dataset-list.component').then(m => m.DatasetListComponent) },
	{ path: 'datasets/:datasetName', canActivate: [authGuard], loadComponent: () => import('./pages/dataset-view/dataset-view.component').then(m => m.DatasetViewComponent) },
	{ path: 'datasets/:datasetName/nodes/:nodeName', canActivate: [authGuard], loadComponent: () => import('./pages/node-view/node-view.component').then(m => m.NodeViewComponent) },
	{ path: 'datasets/:datasetName/nodes/:nodeName/sensors/:sensorName', canActivate: [authGuard], loadComponent: () => import('./pages/sensor-view/sensor-view.component').then(m => m.SensorViewComponent) },
	{ path: 'tokens', canActivate: [authGuard], loadComponent: () => import('./pages/token-list/token-list.component').then(m => m.TokenListComponent) },
	{ path: 'users', canActivate: [adminGuard], loadComponent: () => import('./pages/user-list/user-list.component').then(m => m.UserListComponent) },
	{ path: 'users/:username', canActivate: [authGuard], loadComponent: () => import('./pages/user-view/user-view.component').then(m => m.UserViewComponent) },
	{ path: 'timeseries', canActivate: [adminGuard], loadComponent: () => import('./pages/timeserie-list/timeserie-list.component').then(m => m.TimeserieListComponent) },
	{ path: 'broker', canActivate: [adminGuard], loadComponent: () => import('./pages/broker-view/broker-view.component').then(m => m.BrokerViewComponent) },
	{ path: 'settings', canActivate: [adminGuard], loadComponent: () => import('./pages/settings-view/settings-view.component').then(m => m.SettingsViewComponent) },
	{ path: '', canActivate: [authGuard], loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent) },
	{ path: '**', redirectTo: '' }
];
