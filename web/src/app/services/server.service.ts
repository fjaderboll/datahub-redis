import { Injectable, inject } from '@angular/core';
import { UtilsService } from './utils.service';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Dataset, DatasetNode, Overview, Reading, Sensor, Settings, SystemState, Timeserie, Token, User, UsersState } from '../models';

/**
 * Builds an API URL where every interpolated value is encoded as one path segment,
 * so names taken from the page URL can not point the request at another endpoint.
 * Example: api`datasets/${datasetName}/nodes`
 */
function api(strings: TemplateStringsArray, ...values: string[]) {
	return environment.apiUrl + strings.reduce((url, s, i) => url + encodeURIComponent(values[i - 1]) + s);
}

@Injectable({
  providedIn: 'root'
})
export class ServerService {
	private http = inject(HttpClient);
	private utils = inject(UtilsService);

	public showHttpError(error: HttpErrorResponse) {
		if(error.status === 401) {
			return; // the session has ended, which the auth interceptor tells the user about
		}
		if(error.status === 0) {
			this.utils.toastError("Cannot reach the server");
			return;
		}
		if(error.error && (typeof error.error === 'string' || error.error instanceof String)) {
			try {
				const data = JSON.parse(error.error as string);
				if(data.message) {
					this.utils.toastError(data.message);
					return;
				}
			} catch (e) {}
			this.utils.toastError(error.error as string);
		} else if(error.error?.message) {
			this.utils.toastError(error.error.message);
		} else {
			this.utils.toastError(error.message);
		}
	}

	// ----- State -----

	public getStateUsers() {
		return this.http.get<UsersState>(api`state/users`);
	}

	public getStateSystem() {
		return this.http.get<SystemState>(api`state/system`);
	}

	public getStateSettings() {
		return this.http.get<Settings>(api`state/settings`);
	}

	public updateStateSettings(setting: string, value: any) {
		return this.http.put<string>(api`state/settings`, { [setting]: value });
	}

	public getStateTimeseries() {
		return this.http.get<Timeserie[]>(api`state/timeseries`);
	}

	public getStateOverview() {
		return this.http.get<Overview>(api`state/overview`);
	}

	/**
	 * Readings as they are created. The response never ends, so it is read with fetch
	 * one line at a time instead of HttpClient, which would keep the whole response in memory.
	 */
	public streamReadings(token: string) {
		return new Observable<Reading>(subscriber => {
			const controller = new AbortController();

			const read = async () => {
				const response = await fetch(api`state/readings`, {
					headers: { Authorization: 'Bearer ' + token },
					signal: controller.signal
				});
				if(!response.ok || !response.body) {
					throw new HttpErrorResponse({ status: response.status, statusText: response.statusText, url: response.url, error: await response.text() });
				}

				const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
				let buffer = '';
				while(true) {
					const { value, done } = await reader.read();
					if(done) {
						break;
					}
					buffer += value;
					const lines = buffer.split('\n');
					buffer = lines.pop() ?? ''; // incomplete line, the rest arrives with the next chunk
					lines.filter(line => line.trim()).forEach(line => subscriber.next(JSON.parse(line)));
				}
				subscriber.complete();
			};

			read().catch(e => {
				if(!controller.signal.aborted) {
					subscriber.error(e instanceof HttpErrorResponse ? e : new HttpErrorResponse({ error: e }));
				}
			});

			return () => controller.abort();
		});
	}

	// ----- Users -----

	public login(username: string, password: string) {
		return this.http.post<Token>(api`users/${username}/login`, { password, referrer: 'Web login' });
	}

	public logout(username: string, token: string) {
		return this.http.post<string>(api`users/${username}/logout`, {}, { headers: { Authorization: 'Bearer ' + token } });
	}

	public impersonate(username: string) {
		return this.http.post<Token>(api`users/${username}/impersonate`, {});
	}

	public getUsers() {
		return this.http.get<User[]>(api`users/`);
	}

	public getUser(username: string) {
		return this.http.get<User>(api`users/${username}`);
	}

	public updateUser(username: string, property: string, value: any) {
		return this.http.put<User>(api`users/${username}`, { [property]: value });
	}

	public createUser(username: string, password: string) {
		return this.http.post<User>(api`users/`, { username, password });
	}

	public deleteUser(username: string) {
		return this.http.delete<string>(api`users/${username}`);
	}

	// ----- Token -----

	public createToken(description: string, ttl: number | null) {
		return this.http.post<Token>(api`tokens/`, { desc: description, ttl });
	}

	public getTokens() {
		return this.http.get<Token[]>(api`tokens/`);
	}

	public updateToken(id: string, property: string, value: any) {
		return this.http.put<Token>(api`tokens/${id}`, { [property]: value });
	}

	public deleteToken(id: string) {
		return this.http.delete<string>(api`tokens/${id}`);
	}

	// ----- Datasets -----

	public createDataset(name: string, description: string) {
		return this.http.post<Dataset>(api`datasets/`, { name, desc: description });
	}

	public getDatasets() {
		return this.http.get<Dataset[]>(api`datasets/`);
	}

	public getDataset(name: string) {
		return this.http.get<Dataset>(api`datasets/${name}`);
	}

	public updateDataset(name: string, property: string, value: any) {
		return this.http.put<Dataset>(api`datasets/${name}`, { [property]: value });
	}

	public deleteDataset(name: string) {
		return this.http.delete<string>(api`datasets/${name}`);
	}

	public getDatasetUsers(name: string) {
		return this.http.get<string[]>(api`datasets/${name}/users`);
	}

	public shareDataset(datasetName: string, username: string) {
		return this.http.post<string>(api`datasets/${datasetName}/users`, { username });
	}

	public unshareDataset(datasetName: string, username: string) {
		return this.http.delete<string>(api`datasets/${datasetName}/users/${username}`);
	}

	public getDatasetUnits(datasetName: string) {
		return this.http.get<string[]>(api`datasets/${datasetName}/units`);
	}

	// ----- Nodes -----

	public createNode(datasetName: string, nodeName: string, description: string) {
		return this.http.post<DatasetNode>(api`datasets/${datasetName}/nodes`, { name: nodeName, desc: description });
	}

	public getNodes(datasetName: string) {
		return this.http.get<DatasetNode[]>(api`datasets/${datasetName}/nodes`);
	}

	public getNode(datasetName: string, nodeName: string) {
		return this.http.get<DatasetNode>(api`datasets/${datasetName}/nodes/${nodeName}`);
	}

	public updateNode(datasetName: string, nodeName: string, property: string, value: any) {
		return this.http.put<DatasetNode>(api`datasets/${datasetName}/nodes/${nodeName}`, { [property]: value });
	}

	public deleteNode(datasetName: string, nodeName: string) {
		return this.http.delete<string>(api`datasets/${datasetName}/nodes/${nodeName}`);
	}

	// ----- Sensor -----

	public createSensor(datasetName: string, nodeName: string, sensorName: string, description: string, unit: string) {
		return this.http.post<Sensor>(api`datasets/${datasetName}/nodes/${nodeName}/sensors`, { name: sensorName, desc: description, unit });
	}

	public getSensors(datasetName: string, nodeName: string) {
		return this.http.get<Sensor[]>(api`datasets/${datasetName}/nodes/${nodeName}/sensors`);
	}

	public getSensor(datasetName: string, nodeName: string, sensorName: string) {
		return this.http.get<Sensor>(api`datasets/${datasetName}/nodes/${nodeName}/sensors/${sensorName}`);
	}

	public updateSensor(datasetName: string, nodeName: string, sensorName: string, property: string, value: any) {
		return this.http.put<Sensor>(api`datasets/${datasetName}/nodes/${nodeName}/sensors/${sensorName}`, { [property]: value });
	}

	public deleteSensor(datasetName: string, nodeName: string, sensorName: string) {
		return this.http.delete<string>(api`datasets/${datasetName}/nodes/${nodeName}/sensors/${sensorName}`);
	}

	// ----- Readings -----

	public createReading(datasetName: string, nodeName: string, sensorName: string, value: number, time: string | null) {
		const reading: { value: number, time?: string } = { value };
		if(time) {
			reading.time = time;
		}
		return this.http.post<Reading[]>(api`datasets/${datasetName}/nodes/${nodeName}/sensors/${sensorName}/readings`, [reading]);
	}

	public getSensorReadings(datasetName: string, nodeName: string, sensorName: string, limit: number | null, after: string | null) {
		const params = this.getReadingsParams(limit, after);
		return this.http.get<Reading[]>(api`datasets/${datasetName}/nodes/${nodeName}/sensors/${sensorName}/readings`, { params });
	}

	public getNodeReadings(datasetName: string, nodeName: string, limit: number | null, after: string | null) {
		const params = this.getReadingsParams(limit, after);
		return this.http.get<Reading[]>(api`datasets/${datasetName}/nodes/${nodeName}/readings`, { params });
	}

	public getDatasetReadings(datasetName: string, limit: number | null, after: string | null) {
		const params = this.getReadingsParams(limit, after);
		return this.http.get<Reading[]>(api`datasets/${datasetName}/readings`, { params });
	}

	public getReadings(limit: number | null, after: string | null) {
		const params = this.getReadingsParams(limit, after);
		return this.http.get<Reading[]>(api`readings/`, { params });
	}

	private getReadingsParams(limit: number | null, after: string | null) {
		let params = new HttpParams();
		if(limit !== null) {
			params = params.set('limit', limit);
		}
		if(after !== null) {
			params = params.set('after', after);
		}
		return params;
	}

	public deleteReadings(datasetName: string, nodeName: string, sensorName: string) {
		return this.http.delete<string>(api`datasets/${datasetName}/nodes/${nodeName}/sensors/${sensorName}/readings`);
	}

}
