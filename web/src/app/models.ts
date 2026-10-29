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
	mqttOnly: boolean;
	expire: string | null;
	desc: string | null;
	token: string;
	username: string;
	isAdmin: boolean;
}

export interface Dataset {
	name: string;
	desc: string;
	/** Only in the list of datasets */
	nodeCount?: number;
	nodes?: DatasetNode[];
}

// not named Node, which would shadow the DOM type
export interface DatasetNode {
	name: string;
	desc: string;
	/** Only in lists of nodes */
	sensorCount?: number;
	/** Only in lists of nodes, newest reading of all its sensors */
	lastTimestamp?: string | null;
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

export interface Overview {
	datasets: number;
	nodes: number;
	sensors: number;
	readings24h: number;
	silentSensors: number;
	/** Newest last reading first */
	recentNodes: NodeActivity[];
	/** Nodes with at least one silent sensor, the most recently quiet first */
	silentNodes: NodeActivity[];
}

export interface NodeActivity {
	datasetName: string;
	nodeName: string;
	lastTimestamp: string;
	sensors: SensorActivity[];
}

export interface SensorActivity {
	name: string;
	unit: string;
	lastReading: Reading | null;
	/** Usual seconds between readings, null until there are enough readings to tell */
	interval: number | null;
	/** Quiet for much longer than the usual interval */
	silent: boolean;
}
