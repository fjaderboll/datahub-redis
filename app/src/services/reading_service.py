from parser import ParserError
import dateutil.parser as dp
from datetime import datetime
import json

from flask_restx import abort
from flask import request

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

def parseLimit(limit, defaultValue):
	if limit:
		try:
			l = int(limit)
			if l < 0:
				abort(400, 'Invalid limit: ' + limit)
			return l
		except ValueError:
			abort(400, 'Invalid limit: ' + limit)
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

def getReadings(auth, datasetName, nodeName, sensorName):
	dataset = None
	node = None
	sensor = None

	if datasetName:
		dataset = finder.findDataset(auth, datasetName)
	if nodeName:
		node = finder.findNode(dataset['id'], nodeName)
	if sensorName:
		sensor = finder.findSensor(node['id'], sensorName)

	requestedSensors = findRequestedSensors(auth, dataset, node, sensor)

	after = request.args.get('after')
	before = request.args.get('before')
	limit = request.args.get('limit')

	fromTime = parseTime(after, '-')
	toTime = parseTime(before, '+')
	count = parseLimit(limit, None)

	readings = []
	c = None
	for requestedSensor in requestedSensors:
		if count is not None:
			c = count - len(readings)
			if c <= 0:
				break

		if not datasetName:
			dataset = db.hgetall(Keys.getDatasetById(requestedSensor['datasetId']))
		if not nodeName:
			node = db.hgetall(Keys.getNodeById(requestedSensor['nodeId']))
		if not sensorName:
			sensor = db.hgetall(Keys.getSensorById(requestedSensor['sensorId']))

		items = ts.range(Keys.getReadings(requestedSensor['sensorId']), fromTime, toTime, count=c)
		readings.extend(cleaner.cleanReadings(items, dataset, node, sensor))

	return readings

def deleteReadings(auth, datasetName, nodeName, sensorName):
	dataset = None
	node = None
	sensor = None

	if datasetName:
		dataset = finder.findDataset(auth, datasetName)
	if nodeName:
		node = finder.findNode(dataset['id'], nodeName)
	if sensorName:
		sensor = finder.findSensor(node['id'], sensorName)

	requestedSensors = findRequestedSensors(auth, dataset, node, sensor)

	after = request.args.get('after')
	before = request.args.get('before')

	fromTime = parseTime(after, '-')
	toTime = parseTime(before, '+')

	n = 0
	for requestedSensor in requestedSensors:
		n += ts.delete(Keys.getReadings(requestedSensor['sensorId']), fromTime, toTime)

	return "Removed " + str(n) + " readings"

def findRequestedSensors(auth, dataset, node, sensor):
	requestedSensors = []
	if sensor:
		requestedSensors.append({
			'sensorId': sensor['id'],
			'nodeId': node['id'],
			'datasetId': dataset['id']
		})
	elif node:
		sensorIds = db.smembers(Keys.getNodeSensorIds(node['id']))
		for sensorId in sensorIds:
			requestedSensors.append({
				'sensorId': sensorId,
				'nodeId': node['id'],
				'datasetId': dataset['id']
			})
	elif dataset:
		nodeIds = db.smembers(Keys.getDatasetNodeIds(dataset['id']))
		for nodeId in nodeIds:
			sensorIds = db.smembers(Keys.getNodeSensorIds(nodeId))
			for sensorId in sensorIds:
				requestedSensors.append({
					'sensorId': sensorId,
					'nodeId': nodeId,
					'datasetId': dataset['id']
				})
	else:
		datasetIds = db.smembers(Keys.getUserDatasetIds(auth['username']))
		for datasetId in datasetIds:
			nodeIds = db.smembers(Keys.getDatasetNodeIds(datasetId))
			for nodeId in nodeIds:
				sensorIds = db.smembers(Keys.getNodeSensorIds(nodeId))
				for sensorId in sensorIds:
					requestedSensors.append({
						'sensorId': sensorId,
						'nodeId': nodeId,
						'datasetId': datasetId
					})

	return requestedSensors

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
