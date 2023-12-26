import { Injectable } from '@angular/core';
import { ToastrService } from 'ngx-toastr';

@Injectable({
  providedIn: 'root'
})
export class UtilsService {

	constructor(
		private toastr: ToastrService
	) { }

	public toastSuccess(message: string) {
		this.toastr.success(message);
	}

	public toastWarn(message: string) {
		this.toastr.warning(message);
	}

	public toastError(message: string) {
		console.log(message);
		this.toastr.error(message);
	}

	public printFilesize(bytes: number, decimals?: number) {
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

	public toDate(timestamp: string) {
		if(timestamp) {
			return new Date(timestamp);
		}
		return null;
	}

	public printTimestamp(timestamp: string) {
		let date = this.toDate(timestamp);
		if(date) {
			return date.toLocaleString("sv-SE");
		}
		return null;
	}

	public getRelativeTime(timestamp: string) {
		if(timestamp) {
	        let time = Date.now() - new Date(timestamp).getTime();
	        let futureDate = (time < 0);
	        time = Math.abs(time);
			if(time < 1000) {
				return "just now";
			}
	        let multipliers = [1000, 60, 60, 24, 7, 4.32, 12, Infinity];
	        let units = ["ms", "second", "minute", "hour", "day", "week", "month", "year"];

	        for(let i = 0; i < multipliers.length; i++) {
				let t = Math.floor(time);
	            if(t < multipliers[i] || i == multipliers.length - 1) {
	                return t + " " + units[i] + (t == 1 ? "" : "s") + " " + (futureDate ? "left" : "ago");
	            }
	            time /= multipliers[i];
	        }
		}
		return "";
    }

}
