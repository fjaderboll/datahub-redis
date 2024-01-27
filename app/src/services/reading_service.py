from parser import ParserError
import dateutil.parser as dp
from datetime import datetime
import json

from flask_restx import abort

from api import api
from db import db, ts, Keys
from services import cleaner, finder

def parseTime(time, defaultValue):
	if time:
		try:
			offset = float(time)
			return int(datetime.now().timestamp()*1000 + offset*1000)
		except ValueError:
			try:
				return int(dp.parse(time).timestamp()*1000)
			except ParserError:
				abort(400, 'Invalid time: ' + time)
	return defaultValue

def createReadings(auth, datasetName, nodeName, sensorName):
	dataset = None
	node = None
	sensor = None

	if datasetName:
		dataset = finder.findDataset(auth, datasetName, create=True)
	if nodeName:
		node = finder.findNode(dataset['id'], nodeName, create=True)
	if sensorName:
		sensor = finder.findSensor(node['id'], sensorName, create=True)

	readings = []
	for reading in api.payload:
		value = reading['value']
		time = reading['time'] if 'time' in reading else None

		if not datasetName:
			dataset = finder.findDataset(auth, reading['datasetName'], create=True)
		if not nodeName:
			node = finder.findNode(dataset['id'], reading['nodeName'], create=True)
		if not sensorName:
			sensor = finder.findSensor(node['id'], reading['sensorName'], create=True)

		cleanedReading = createReading(dataset, node, sensor, value, time=time)
		readings.append(cleanedReading)

	return readings

def createReading(dataset, node, sensor, value, time=None):
	timestamp = parseTime(time, '*')

	key = Keys.getReadings(sensor['id'])
	ts.add(key, timestamp, value)
	reading = ts.get(key)
	cleanedReading = cleaner.cleanReading(reading, dataset, node, sensor)
	db.publish(Keys.getReadingsTopic(), json.dumps(cleanedReading))
	return cleanedReading

def getReadings(sensorId, after=None, before=None, limit=None):
	fromTime = parseTime(after, '-')
	toTime = parseTime(before, '+')
	count = int(limit) if limit else None

	items = ts.range(Keys.getReadings(sensorId), fromTime, toTime, count=count)
	return items

def deleteReadings(sensorId, after=None, before=None):
	fromTime = parseTime(after, '-')
	toTime = parseTime(before, '+')

	return ts.delete(Keys.getReadings(sensorId), fromTime, toTime)

def getLastReading(sensorId):
	return ts.get(Keys.getReadings(sensorId))

def getReadingStats(sensorId):
	info = ts.info(Keys.getReadings(sensorId))
	return {
		'memory': info.memory_usage,
		'count': info.total_samples,
		'retention': int(info.retention_msecs / 1000)
		#'lastTimestamp': info.last_time_stamp,
		#'firstTimestamp': info.first_time_stamp
	}
