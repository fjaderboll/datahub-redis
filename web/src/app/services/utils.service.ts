import { Injectable, inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

/** Valid user, dataset, node and sensor names, as checked by the backend. */
export const NAME_PATTERN = '[a-z0-9][a-z0-9_@.\\-]*[a-z0-9]';

@Injectable({
  providedIn: 'root'
})
export class UtilsService {
	private snackBar = inject(MatSnackBar);

	public toastSuccess(message: string) {
		this.toast(message, 'toast-success', 3000);
	}

	public toastWarn(message: string) {
		this.toast(message, 'toast-warn', 6000);
	}

	public toastError(message: string) {
		this.toast(message, 'toast-error', 6000);
	}

	private toast(message: string, panelClass: string, duration: number) {
		this.snackBar.open(message, 'OK', {
			duration,
			panelClass,
			horizontalPosition: 'end'
		});
	}

	public printFilesize(bytes: number | null | undefined, decimals?: number) {
		if(bytes == null) return '';
		if(bytes === 0) return '0 Bytes';
		if(bytes === 1) return '1 Byte';

		let k = 1024; // or 1024 for binary
		let sizes = ['Bytes', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
		let decimalArray = [0, 0, 1, 2, 3, 3, 3, 3, 3];

		let i = Math.floor(Math.log(bytes) / Math.log(k));
		let dm = decimals ? decimals : decimalArray[i];
		return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
	}

	public toDate(timestamp: string | null | undefined) {
		if(timestamp) {
			return new Date(timestamp);
		}
		return null;
	}

	public printTimestamp(timestamp: string | null | undefined) {
		let date = this.toDate(timestamp);
		if(date) {
			return date.toLocaleString("sv-SE");
		}
		return null;
	}

	public getRelativeTime(timestamp: string | null | undefined) {
		if(timestamp) {
			let time = Date.now() - new Date(timestamp).getTime();
			let futureDate = (time < 0);
			time = Math.abs(time);
			if(time < 1000) {
				return "just now";
			}
			return this.getDeltaTime(time) + " " + (futureDate ? "left" : "ago");
		}
		return "";
	}

	public getDeltaTime(milliseconds: number) {
		let time = milliseconds;
		let multipliers = [1000, 60, 60, 24, 7, 4.32, 12, Infinity];
		let units = ["millisecond", "second", "minute", "hour", "day", "week", "month", "year"];

		for(let i = 0; i < multipliers.length; i++) {
			let t = Math.floor(time);
			if(t < multipliers[i] || i == multipliers.length - 1) {
				return t + " " + units[i] + (t == 1 ? "" : "s");
			}
			time /= multipliers[i];
		}
		return ""
	}

	/** A duration in seconds, where 0 means there is no limit (as for retention and token TTL). */
	public printDuration(seconds: number | null | undefined, unlimitedText: string) {
		if(seconds == null || isNaN(seconds)) {
			return "";
		}
		if(seconds == 0) {
			return unlimitedText;
		}
		return this.getDeltaTime(seconds * 1000);
	}

}
