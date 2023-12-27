import util
import datetime
import pytz

def cleanUser(user):
	return cleanUsers([user])[0]

def cleanUsers(users):
	cleanedUsers = []
	for user in users:
		cleanedUser = util.copy(user, ['username', 'email', 'isAdmin'])
		cleanedUsers.append(cleanedUser)
	return cleanedUsers

def cleanDataset(dataset):
	return cleanDatasets([dataset])[0]

def cleanDatasets(datasets):
	cleanedDatasets = []
	for dataset in datasets:
		cleanedDataset = util.cleanObject(dataset, ['name', 'desc'])
		cleanedDatasets.append(cleanedDataset)
	return cleanedDatasets

def cleanNode(node):
	return util.cleanObject(node, ['name', 'desc', 'sensors'])

def cleanSensor(sensor):
	return cleanSensors([sensor])[0]

def cleanSensors(sensors):
	cleanedSensors = []
	for sensor in sensors:
		cleanedSensor = util.cleanObject(sensor, ['name', 'desc', 'unit', 'lastReading', 'readingStats'])
		cleanedSensors.append(cleanedSensor)
	return cleanedSensors

def cleanReading(reading, dataset, node, sensor):
	if reading:
		return cleanReadings([reading], dataset, node, sensor)[0]
	return None

def cleanReadings(readings, dataset, node, sensor):
	cleanedReadings = []
	for reading in readings:
		cleanedReading = {
			'timestamp': datetime.datetime.fromtimestamp(reading[0] / 1000).astimezone(pytz.UTC).isoformat(),
			'value': reading[1],
			'datasetName': dataset['name'],
			'nodeName': node['name'],
			'sensorName': sensor['name'],
			'unit': sensor['unit']
		}
		cleanedReadings.append(cleanedReading)
	return cleanedReadings
