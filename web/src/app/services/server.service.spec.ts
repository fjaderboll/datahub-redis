import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ServerService } from './server.service';
import { environment } from '../../environments/environment';
import { Reading } from '../models';

describe('ServerService', () => {
	const api = environment.apiUrl;
	let server: ServerService;
	let http: HttpTestingController;

	beforeEach(() => {
		TestBed.configureTestingModule({
			providers: [provideHttpClient(), provideHttpClientTesting()]
		});
		server = TestBed.inject(ServerService);
		http = TestBed.inject(HttpTestingController);
	});

	afterEach(() => {
		http.verify();
	});

	it('encodes each name as one path segment', () => {
		server.deleteSensor('home', 'kitchen', '../../../../users/bob').subscribe();
		const req = http.expectOne(api + 'datasets/home/nodes/kitchen/sensors/..%2F..%2F..%2F..%2Fusers%2Fbob');
		expect(req.request.method).toBe('DELETE');
		req.flush("Removed sensor");
	});

	it('reads messages as JSON, so they come without quotes', () => {
		server.deleteDataset('home').subscribe();
		const req = http.expectOne(api + 'datasets/home');
		expect(req.request.responseType).toBe('json');
		req.flush("Removed dataset 'home'");
	});

	it('adds reading query parameters', () => {
		server.getDatasetReadings('home', 0, '-3600').subscribe();
		const req = http.expectOne(r => r.url == api + 'datasets/home/readings');
		expect(req.request.params.get('limit')).toBe('0');
		expect(req.request.params.get('after')).toBe('-3600');
		req.flush([]);
	});

	describe('streamReadings', () => {
		function mockFetch(chunks: string[], status = 200) {
			const encoder = new TextEncoder();
			const body = new ReadableStream<Uint8Array>({
				start(controller) {
					chunks.forEach(chunk => controller.enqueue(encoder.encode(chunk)));
					controller.close();
				}
			});
			return vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(body, { status }));
		}

		afterEach(() => {
			vi.restoreAllMocks();
		});

		it('emits every reading when lines are split and combined across chunks', async () => {
			const line = (value: number) => JSON.stringify({ value, datasetName: 'home' });
			const fetchSpy = mockFetch([
				line(1) + '\n' + line(2) + '\n' + line(3).slice(0, 5),
				line(3).slice(5) + '\n',
				line(4) + '\n'
			]);

			const values = await new Promise<number[]>((resolve, reject) => {
				const received: number[] = [];
				server.streamReadings('secret').subscribe({
					next: (reading: Reading) => received.push(reading.value),
					complete: () => resolve(received),
					error: reject
				});
			});

			expect(values).toEqual([1, 2, 3, 4]);
			expect(fetchSpy.mock.calls[0][1]?.headers).toEqual({ Authorization: 'Bearer secret' });
		});

		it('reports HTTP errors with their status', async () => {
			mockFetch(['{"message": "Unauthorized"}'], 401);
			const error = await new Promise<any>(resolve => server.streamReadings('old').subscribe({ error: resolve }));
			expect(error.status).toBe(401);
		});
	});
});
