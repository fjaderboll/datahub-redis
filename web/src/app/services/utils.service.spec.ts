import { TestBed } from '@angular/core/testing';
import { UtilsService } from './utils.service';

describe('UtilsService', () => {
	let utils: UtilsService;

	beforeEach(() => {
		utils = TestBed.inject(UtilsService);
	});

	it('prints file sizes', () => {
		expect(utils.printFilesize(0)).toBe('0 Bytes');
		expect(utils.printFilesize(1)).toBe('1 Byte');
		expect(utils.printFilesize(1536)).toBe('2 kB');
		expect(utils.printFilesize(5 * 1024 * 1024)).toBe('5 MB');
		expect(utils.printFilesize(null)).toBe('');
	});

	it('prints durations', () => {
		expect(utils.getDeltaTime(1000)).toBe('1 second');
		expect(utils.getDeltaTime(90 * 60 * 1000)).toBe('1 hour');
		expect(utils.getDeltaTime(3 * 3600 * 1000)).toBe('3 hours');
	});

	it('prints 0 as no limit', () => {
		expect(utils.printDuration(0, 'forever')).toBe('forever');
		expect(utils.printDuration(86400, 'forever')).toBe('1 day');
		expect(utils.printDuration(undefined, 'forever')).toBe('');
	});

	it('prints relative times', () => {
		expect(utils.getRelativeTime(new Date(Date.now() - 5 * 60 * 1000).toISOString())).toBe('5 minutes ago');
		expect(utils.getRelativeTime(new Date(Date.now() + 2 * 3600 * 1000 + 5000).toISOString())).toBe('2 hours left');
		expect(utils.getRelativeTime(null)).toBe('');
	});
});
