import { Injectable } from '@angular/core';
import { UtilsService } from './utils.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ServerService {
	private apiUrl: string;
	private httpOptionsJson: any;
	private httpOptionsText: any;
	private httpOptionsStream: any;

	constructor(
		private http: HttpClient,
		private utils: UtilsService
	) {
		this.apiUrl = environment.apiUrl;
	}

	public setToken(token: string | null) {
		let headers = new HttpHeaders({
			'Content-Type': 'application/json'
		});
        if(token) {
            headers = headers.set('Authorization', ' Bearer ' + token)
        }
		this.httpOptionsJson = {
			headers,
			responseType: 'json'
		};
		this.httpOptionsText = {
			headers,
			responseType: 'text'
		};
		this.httpOptionsStream = {
			headers,
			responseType: 'text',
			observe: 'events',
			reportProgress: true
		};
	}

	public showHttpError(error: any) {
		console.log(error);
		if(error.error && (typeof error.error === 'string' || error.error instanceof String)) {
            try {
                const data = JSON.parse(error.error);
                if(data.message) {
                    this.utils.toastError(data.message);
                    return;
                }
            } catch (e) {}
			this.utils.toastError(error.error);
        } else if(error.error?.message) {
            this.utils.toastError(error.error.message);
        } else {
			this.utils.toastError(error.message);
		}
	}

	// ----- State -----

    public getStateUsers() {
		const url = this.apiUrl + "state/users";
		return this.http.get(url, this.httpOptionsJson);
	}

	public getStateSystem() {
		const url = this.apiUrl + "state/system";
		return this.http.get(url, this.httpOptionsJson);
	}

	public getStateSettings() {
		const url = this.apiUrl + "state/settings";
		return this.http.get(url, this.httpOptionsJson);
	}

	public updateStateSettings(setting: string, value: any) {
		const url = this.apiUrl + "state/settings";
		return this.http.put(url, { [setting]: value }, this.httpOptionsText);
	}

	public getStateTimeseries() {
		const url = this.apiUrl + "state/timeseries";
		return this.http.get(url, this.httpOptionsJson);
	}

	public getStateReadings() {
		const url = this.apiUrl + "state/readings";
		return this.http.get(url, this.httpOptionsStream);
	}

    // ----- Users -----

	public login(username: string, password: string) {
		const url = this.apiUrl + "users/" + username + "/login";
		return this.http.post(url, { password }, this.httpOptionsJson);
	}

    public logout(username: string) {
		const url = this.apiUrl + "users/" + username + "/logout";
		return this.http.post(url, {}, this.httpOptionsText);
	}

	public impersonate(username: string) {
		const url = this.apiUrl + "users/" + username + "/impersonate";
		return this.http.post(url, {}, this.httpOptionsJson);
	}

    public getUsers() {
		const url = this.apiUrl + "users/";
		return this.http.get(url, this.httpOptionsJson);
	}

	public getUser(username: string) {
		const url = this.apiUrl + "users/" + username;
		return this.http.get(url, this.httpOptionsJson);
	}

	public updateUser(username: string, property: string, value: any) {
		const url = this.apiUrl + "users/" + username;
		return this.http.put(url, { [property]: value }, this.httpOptionsText);
	}

	public createUser(username: string, password: string) {
		const url = this.apiUrl + "users/";
		return this.http.post(url, { username, password }, this.httpOptionsJson);
	}

	public deleteUser(username: string) {
		const url = this.apiUrl + "users/" + username;
		return this.http.delete(url, this.httpOptionsText);
	}

    // ----- Token -----

    public createToken(description: string, ttl: number | null) {
		const url = this.apiUrl + "tokens/";
		return this.http.post(url, { desc: description, ttl }, this.httpOptionsJson);
	}

    public getTokens() {
		const url = this.apiUrl + "tokens/";
		return this.http.get(url, this.httpOptionsJson);
	}

	public updateToken(id: string, property: string, value: any) {
		const url = this.apiUrl + "tokens/" + id;
		return this.http.put(url, { [property]: value }, this.httpOptionsText);
	}

	public deleteToken(id: string) {
		const url = this.apiUrl + "tokens/" + id;
		return this.http.delete(url, this.httpOptionsText);
	}

    // ----- Datasets -----

    public createDataset(name: string, description: string) {
		const url = this.apiUrl + "datasets/";
		return this.http.post(url, { name, desc: description }, this.httpOptionsJson);
	}

    public getDatasets() {
		const url = this.apiUrl + "datasets/";
		return this.http.get(url, this.httpOptionsJson);
	}

	public getDataset(name: string) {
		const url = this.apiUrl + "datasets/" + name;
		return this.http.get(url, this.httpOptionsJson);
	}

	public updateDataset(name: string, property: string, value: any) {
		const url = this.apiUrl + "datasets/" + name;
		return this.http.put(url, { [property]: value }, this.httpOptionsText);
	}

	public deleteDataset(name: string) {
		const url = this.apiUrl + "datasets/" + name;
		return this.http.delete(url, this.httpOptionsText);
	}

	public getDatasetUsers(name: string) {
		const url = this.apiUrl + "datasets/" + name + "/users";
		return this.http.get(url, this.httpOptionsJson);
	}

	public shareDataset(datasetName: string, username: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/users";
		return this.http.post(url, { username }, this.httpOptionsText);
	}

	public unshareDataset(datasetName: string, username: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/users/" + username;
		return this.http.delete(url, this.httpOptionsText);
	}

    // ----- Nodes -----

    public createNode(datasetName: string, nodeName: string, description: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes";
		return this.http.post(url, { name: nodeName, desc: description }, this.httpOptionsJson);
	}

    public getNodes(datasetName: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes";
		return this.http.get(url, this.httpOptionsJson);
	}

	public getNode(datasetName: string, nodeName: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName;
		return this.http.get(url, this.httpOptionsJson);
	}

	public updateNode(datasetName: string, nodeName: string, property: string, value: any) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName;
		return this.http.put(url, { [property]: value }, this.httpOptionsText);
	}

	public deleteNode(datasetName: string, nodeName: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName;
		return this.http.delete(url, this.httpOptionsText);
	}

    // ----- Sensor -----

    public createSensor(datasetName: string, nodeName: string, sensorName: string, description: string, unit: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName + "/sensors";
		return this.http.post(url, { name: sensorName, desc: description, unit }, this.httpOptionsJson);
	}

    public getSensors(datasetName: string, nodeName: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName + "/sensors";
		return this.http.get(url, this.httpOptionsJson);
	}

	public getSensor(datasetName: string, nodeName: string, sensorName: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName + "/sensors/" + sensorName;
		return this.http.get(url, this.httpOptionsJson);
	}

	public updateSensor(datasetName: string, nodeName: string, sensorName: string, property: string, value: any) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName + "/sensors/" + sensorName;
		return this.http.put(url, { [property]: value }, this.httpOptionsText);
	}

	public deleteSensor(datasetName: string, nodeName: string, sensorName: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName + "/sensors/" + sensorName;
		return this.http.delete(url, this.httpOptionsText);
	}

    // ----- Readings -----

    public createReading(datasetName: string, nodeName: string, sensorName: string, value: number, time: string | null) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName + "/sensors/" + sensorName + "/readings";
		return this.http.post(url, { value, time }, this.httpOptionsJson);
	}

    public getSensorReadings(datasetName: string, nodeName: string, sensorName: string, limit: number | null) {
		let url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName + "/sensors/" + sensorName + "/readings";
		if(limit) {
			url += "?limit=" + limit;
		}
		return this.http.get(url, this.httpOptionsJson);
	}

	public getNodeReadings(datasetName: string, nodeName: string, limit: number | null) {
		let url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName + "/readings";
		if(limit) {
			url += "?limit=" + limit;
		}
		return this.http.get(url, this.httpOptionsJson);
	}

	public getDatasetReadings(datasetName: string, limit: number | null) {
		let url = this.apiUrl + "datasets/" + datasetName + "/readings";
		if(limit) {
			url += "?limit=" + limit;
		}
		return this.http.get(url, this.httpOptionsJson);
	}

	public getReadings(limit: number | null) {
		let url = this.apiUrl + "readings/";
		if(limit) {
			url += "?limit=" + limit;
		}
		return this.http.get(url, this.httpOptionsJson);
	}

	public deleteReadings(datasetName: string, nodeName: string, sensorName: string) {
		const url = this.apiUrl + "datasets/" + datasetName + "/nodes/" + nodeName + "/sensors/" + sensorName + "/readings";
		return this.http.delete(url, this.httpOptionsText);
	}

}
