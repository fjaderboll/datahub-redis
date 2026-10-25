// Shapes of the objects returned by the REST API, see the Swagger doc at /api/

export interface UsersState {
	createFirstUserRequired: boolean;
	allowPublicCreateUser: boolean;
}

export interface SystemState {
	cpu: {
		loadAvg: number[];
		count: number;
		percent: number;
	};
	memory: {
		total: number;
		available: number;
		percent: number;
		application: number;
		database: number;
	};
}

export interface Settings {
	retention: number;
	allowPublicCreateUser: boolean;
	allowNonAdminLogin: boolean;
	tokenTTL: number;
}

export interface Timeserie {
	datasetName: string;
	nodeName: string;
	sensorName: string;
	memory: number;
	samples: number;
	retention: number;
}

export interface User {
	username: string;
	email: string;
	isAdmin: boolean;
}

export interface Token {
	id: string;
	enabled: boolean;
	expire: string | null;
	desc: string | null;
	token: string;
	username: string;
	isAdmin: boolean;
}

export interface Dataset {
	name: string;
	desc: string;
	nodes?: DatasetNode[];
}

// not named Node, which would shadow the DOM type
export interface DatasetNode {
	name: string;
	desc: string;
	sensors?: Sensor[];
}

export interface Sensor {
	name: string;
	desc: string;
	unit: string;
	lastReading?: Reading | null;
	readingStats?: ReadingStats;
}

export interface ReadingStats {
	memory: number;
	count: number;
	retention: number;
}

export interface Reading {
	timestamp: string;
	value: number;
	datasetName: string;
	nodeName: string;
	sensorName: string;
	unit: string;
}
