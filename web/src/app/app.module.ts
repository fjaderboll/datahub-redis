import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HeaderComponent } from './components/header/header.component';
import { FooterComponent } from './components/footer/footer.component';
import { HttpClientModule } from '@angular/common/http';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatRadioModule } from '@angular/material/radio';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { FormsModule } from '@angular/forms';
import { ToastrModule } from 'ngx-toastr';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { CreateUserDialogComponent } from './dialogs/create-user-dialog/create-user-dialog.component';
import { UserViewComponent } from './pages/user-view/user-view.component';
import { UserListComponent } from './pages/user-list/user-list.component';
import { ConfirmDialogComponent } from './dialogs/confirm-dialog/confirm-dialog.component';
import { InlineEditComponent } from './components/inline-edit/inline-edit.component';
import { BreadcrumbComponent } from './components/breadcrumb/breadcrumb.component';
import { DatasetViewComponent } from './pages/dataset-view/dataset-view.component';
import { DatasetListComponent } from './pages/dataset-list/dataset-list.component';
import { ExportListComponent } from './pages/export-list/export-list.component';
import { TokenListComponent } from './pages/token-list/token-list.component';
import { NodeViewComponent } from './pages/node-view/node-view.component';
import { CreateDatasetDialogComponent } from './dialogs/create-dataset-dialog/create-dataset-dialog.component';
import { CreateNodeDialogComponent } from './dialogs/create-node-dialog/create-node-dialog.component';
import { CreateTokenDialogComponent } from './dialogs/create-token-dialog/create-token-dialog.component';
import { SensorViewComponent } from './pages/sensor-view/sensor-view.component';
import { CreateSensorDialogComponent } from './dialogs/create-sensor-dialog/create-sensor-dialog.component';
import { CreateReadingDialogComponent } from './dialogs/create-reading-dialog/create-reading-dialog.component';
import { ChartModule } from 'angular-highcharts';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    FooterComponent,
    LoginComponent,
    DashboardComponent,
    CreateUserDialogComponent,
    UserViewComponent,
    UserListComponent,
    ConfirmDialogComponent,
    InlineEditComponent,
    BreadcrumbComponent,
    DatasetViewComponent,
    DatasetListComponent,
    ExportListComponent,
    TokenListComponent,
    NodeViewComponent,
    CreateDatasetDialogComponent,
    CreateNodeDialogComponent,
    CreateTokenDialogComponent,
    SensorViewComponent,
    CreateSensorDialogComponent,
    CreateReadingDialogComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpClientModule,
    MatButtonModule,
    MatDialogModule,
    MatIconModule,
    MatToolbarModule,
    MatFormFieldModule,
    MatInputModule,
    MatRadioModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    FormsModule,
    ToastrModule.forRoot({
		positionClass: 'toast-bottom-right',
		preventDuplicates: true
	}),
	ChartModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
