import util
import datetime
import pytz

def cleanSensor(sensor):
	return util.cleanObject(sensor, ['name', 'desc', 'unit'])

def cleanReading(reading, dataset, node, sensor):
	return cleanReadings([reading], dataset, node, sensor)[0]

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
