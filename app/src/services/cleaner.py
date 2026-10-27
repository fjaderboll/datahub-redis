from datetime import datetime, timezone

from services import util

def cleanUser(user):
	return cleanUsers([user])[0]

def cleanUsers(users):
	cleanedUsers = []
	for user in users:
		cleanedUsers.append({
			'username': user['username'],
			'email': user['email'],
			'isAdmin': bool(user['is_admin'])
		})
	return cleanedUsers

def cleanDataset(dataset):
	return cleanDatasets([dataset])[0]

def cleanDatasets(datasets):
	fields = {'name': 'name', 'desc': 'description', 'nodeCount': 'node_count', 'nodes': 'nodes'}
	return [util.cleanObject(dataset, fields) for dataset in datasets]

def cleanNode(node):
	return cleanNodes([node])[0]

def cleanNodes(nodes):
	fields = {'name': 'name', 'desc': 'description', 'sensorCount': 'sensor_count', 'sensors': 'sensors'}
	return [util.cleanObject(node, fields) for node in nodes]

def cleanSensor(sensor):
	return cleanSensors([sensor])[0]

def cleanSensors(sensors):
	fields = {'name': 'name', 'desc': 'description', 'unit': 'unit', 'lastReading': 'lastReading', 'readingStats': 'readingStats'}
	return [util.cleanObject(sensor, fields) for sensor in sensors]

def cleanReading(reading, datasetName, nodeName, sensor):
	if reading:
		return cleanReadings([reading], datasetName, nodeName, sensor)[0]
	return None

def cleanReadings(readings, datasetName, nodeName, sensor):
	cleanedReadings = []
	for reading in readings:
		cleanedReadings.append({
			'timestamp': datetime.fromtimestamp(reading[0] / 1000, timezone.utc).isoformat(),
			'value': reading[1],
			'datasetName': datasetName,
			'nodeName': nodeName,
			'sensorName': sensor['name'],
			'unit': sensor['unit']
		})
	return cleanedReadings
