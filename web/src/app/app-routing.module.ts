import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { authGuardGuard } from './guards/auth-guard.guard';
import { UserViewComponent } from './pages/user-view/user-view.component';
import { UserListComponent } from './pages/user-list/user-list.component';
import { DatasetListComponent } from './pages/dataset-list/dataset-list.component';
import { DatasetViewComponent } from './pages/dataset-view/dataset-view.component';
import { NodeListComponent } from './pages/node-list/node-list.component';
import { NodeViewComponent } from './pages/node-view/node-view.component';
import { TokenListComponent } from './pages/token-list/token-list.component';
import { ExportListComponent } from './pages/export-list/export-list.component';

const routes: Routes = [
    { path: 'login', component: LoginComponent },
    { path: 'datasets', component: DatasetListComponent, canActivate: [authGuardGuard] },
    { path: 'datasets/:datasetName', component: DatasetViewComponent, canActivate: [authGuardGuard] },
    { path: 'datasets/:datasetName/nodes', component: NodeListComponent, canActivate: [authGuardGuard] },
    { path: 'datasets/:datasetName/nodes/:nodeName', component: NodeViewComponent, canActivate: [authGuardGuard] },
//    { path: 'nodes/:nodeName/sensors/:sensorName', component: SensorViewComponent, canActivate: [AuthGuardService] },
    { path: 'datasets/:datasetName/tokens', component: TokenListComponent, canActivate: [authGuardGuard] },
    { path: 'datasets/:datasetName/exports', component: ExportListComponent, canActivate: [authGuardGuard] },
    { path: 'users', component: UserListComponent, canActivate: [authGuardGuard] },
    { path: 'users/:username', component: UserViewComponent, canActivate: [authGuardGuard] },
    { path: '', component: DashboardComponent, canActivate: [authGuardGuard] },
    { path: '**', redirectTo: '', canActivate: [authGuardGuard] }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
