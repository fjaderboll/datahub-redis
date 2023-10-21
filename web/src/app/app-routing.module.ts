import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { authGuardGuard } from './guards/auth-guard.guard';

const routes: Routes = [
    { path: 'login', component: LoginComponent },
//    { path: 'nodes', component: NodeListComponent, canActivate: [AuthGuardService] },
//    { path: 'nodes/:name', component: NodeViewComponent, canActivate: [AuthGuardService] },
//    { path: 'nodes/:nodeName/sensors/:sensorName', component: SensorViewComponent, canActivate: [AuthGuardService] },
//    { path: 'tokens', component: TokenListComponent, canActivate: [AuthGuardService] },
//    { path: 'exports', component: ExportListComponent, canActivate: [AuthGuardService] },
//    { path: 'users', component: UserListComponent, canActivate: [AuthGuardService] },
//    { path: 'users/:username', component: UserViewComponent, canActivate: [AuthGuardService] },
    { path: '', component: DashboardComponent, canActivate: [authGuardGuard] },
    { path: '**', redirectTo: '', canActivate: [authGuardGuard] }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
