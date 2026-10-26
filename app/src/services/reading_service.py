from datetime import datetime, timezone
import json
import statistics

import dateutil.parser as dp
import redis
from flask_restx import abort
from flask import request

from api import api
import db
import tsdb
from services import cleaner, finder, global_vars

PATTERN_READINGS = 21 # newest readings of a sensor that show how often it reports
SILENT_FACTOR = 3 # a sensor is silent after this many usual intervals without a reading,
SILENT_MIN_MSECS = 5 * 60 * 1000 # but never sooner than this

def parseTime(time, defaultValue):
	if time:
		try:
			offset = float(time)
			return int(datetime.now().timestamp()*1000 + offset*1000)
		except ValueError:
			try:
				return int(dp.parse(time).timestamp()*1000)
			except (dp.ParserError, OverflowError):
				abort(400, 'Invalid time: ' + time)
	return defaultValue

def parseLimit(limit, defaultValue):
	if limit is not None and limit != '':
		try:
			l = int(limit)
			if l < 0:
				abort(400, 'Invalid limit: ' + str(limit))
			elif l == 0:
				return None
			return l
		except ValueError:
			abort(400, 'Invalid limit: ' + str(limit))
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

	cache = {}
	def cached(key, find):
		if key not in cache:
			cache[key] = find()
		return cache[key]

	nextFree = {}
	readings = []
	for reading in api.payload:
		value = reading['value']
		time = reading['time'] if 'time' in reading else None

		if not datasetName:
			name = reading['datasetName']
			dataset = cached(('dataset', name), lambda: finder.findDataset(auth, name, create=True))
		if not nodeName:
			name = reading['nodeName']
			node = cached(('node', dataset['id'], name), lambda: finder.findNode(dataset['id'], name, create=True))
		if not sensorName:
			name = reading['sensorName']
			sensor = cached(('sensor', node['id'], name), lambda: finder.findSensor(node['id'], name, create=True))

		cleanedReading = createReading(dataset, node, sensor, value, time=time, nextFree=nextFree)
		readings.append(cleanedReading)

	return readings

def createReading(dataset, node, sensor, value, time=None, nextFree=None):
	"""Store and publish a reading. 'nextFree' (sensor id -> millisecond) is shared by the readings of one request."""
	key = tsdb.readingsKey(sensor['id'])
	if time:
		storedTimestamp = addReadingAt(key, parseTime(time, None), value, sensor)
	else:
		# readings of the same request continue after each other, so they rarely have to look for a free millisecond
		if nextFree is None:
			nextFree = {}
		now = int(datetime.now().timestamp() * 1000)
		storedTimestamp = tsdb.addAtFreeTimestamp(key, max(now, nextFree.get(sensor['id'], 0)), value)
		nextFree[sensor['id']] = storedTimestamp + 1

	cleanedReading = cleaner.cleanReading((storedTimestamp, float(value)), dataset['name'], node['name'], sensor)
	message = json.dumps(cleanedReading)
	tsdb.redisDb.publish(tsdb.READINGS_TOPIC, message)
	global_vars.mqttClient.publish(message)
	return cleanedReading

def addReadingAt(key, timestamp, value, sensor):
	try:
		return tsdb.ts.add(key, timestamp, value)
	except redis.ResponseError as e:
		if not tsdb.isDuplicateError(e):
			raise
		abort(400, "Sensor '{}' already has a reading at {}".format(sensor['name'], datetime.fromtimestamp(timestamp / 1000, timezone.utc).isoformat()))

def getReadings(auth, datasetName, nodeName, sensorName):
	requestedSensors = findRequestedSensors(auth, datasetName, nodeName, sensorName)

	after = request.args.get('after')
	before = request.args.get('before')
	limit = request.args.get('limit', type=int)

	fromTime = parseTime(after, '-')
	toTime = parseTime(before, '+')
	count = parseLimit(limit, 1000)

	readings = []
	c = None
	for requestedSensor in requestedSensors:
		if count is not None:
			c = count - len(readings)
			if c <= 0:
				break

		try:
			items = tsdb.ts.revrange(tsdb.readingsKey(requestedSensor['id']), fromTime, toTime, count=c)
		except Exception as e:
			if not tsdb.isMissingKeyError(e):
				raise
			items = []
		readings.extend(cleaner.cleanReadings(items, requestedSensor['dataset_name'], requestedSensor['node_name'], requestedSensor))

	return readings

def deleteReadings(auth, datasetName, nodeName, sensorName):
	requestedSensors = findRequestedSensors(auth, datasetName, nodeName, sensorName)

	after = request.args.get('after')
	before = request.args.get('before')

	fromTime = parseTime(after, '-')
	toTime = parseTime(before, '+')

	results = runPerSensor([s['id'] for s in requestedSensors], lambda pipe, key: pipe.delete(key, fromTime, toTime))
	n = sum(r for r in results.values() if r)

	return "Removed " + str(n) + " readings"

def findRequestedSensors(auth, datasetName, nodeName, sensorName):
	dataset = None
	node = None
	sensor = None

	if datasetName:
		dataset = finder.findDataset(auth, datasetName)
	if nodeName:
		node = finder.findNode(dataset['id'], nodeName)
	if sensorName:
		sensor = finder.findSensor(node['id'], sensorName)

	sql = '''
		SELECT s.id, s.name, s.unit, n.name AS node_name, d.name AS dataset_name
		FROM sensors s
		JOIN nodes n ON n.id = s.node_id
		JOIN datasets d ON d.id = n.dataset_id
	'''
	if sensor:
		sql += ' WHERE s.id = ?'
		params = (sensor['id'],)
	elif node:
		sql += ' WHERE n.id = ?'
		params = (node['id'],)
	elif dataset:
		sql += ' WHERE d.id = ?'
		params = (dataset['id'],)
	else:
		sql += '''
			JOIN dataset_users du ON du.dataset_id = d.id
			JOIN users u ON u.id = du.user_id
			WHERE u.username = ?
		'''
		params = (auth['username'],)

	return db.query(sql + ' ORDER BY d.name, n.name, s.name', params)

def runPerSensor(sensorIds, command):
	"""Run a time series command for each sensor in one round trip. Missing series give None."""
	pipe = tsdb.ts.pipeline(transaction=False)
	for sensorId in sensorIds:
		command(pipe, tsdb.readingsKey(sensorId))
	results = pipe.execute(raise_on_error=False) if sensorIds else []

	resultBySensorId = {}
	for sensorId, result in zip(sensorIds, results):
		if isinstance(result, Exception):
			if not tsdb.isMissingKeyError(result):
				raise result
			result = None
		resultBySensorId[sensorId] = result
	return resultBySensorId

def getLastReadings(sensorIds):
	return runPerSensor(sensorIds, lambda pipe, key: pipe.get(key))

def getRecentReadingsMany(sensorIds, count):
	"""The newest 'count' readings of each sensor, newest first."""
	results = runPerSensor(sensorIds, lambda pipe, key: pipe.revrange(key, '-', '+', count=count))
	return {sensorId: result or [] for sensorId, result in results.items()}

def getReadingCountsSince(sensorIds, fromTime):
	"""Number of readings of each sensor from 'fromTime' (milliseconds) and on."""
	bucket = max(int(datetime.now().timestamp() * 1000) - fromTime, 1)
	results = runPerSensor(sensorIds, lambda pipe, key: pipe.range(key, fromTime, '+', aggregation_type='count', bucket_size_msec=bucket))
	return {sensorId: int(sum(count for _, count in result or [])) for sensorId, result in results.items()}

def getUsualInterval(readings):
	"""Median time in milliseconds between readings (newest first), None until there are enough of them to tell."""
	if len(readings) < 3:
		return None
	return statistics.median(newer[0] - older[0] for newer, older in zip(readings, readings[1:]))

def isSilent(readings, now):
	"""Whether a sensor has gone quiet compared to how often it usually reports."""
	interval = getUsualInterval(readings)
	return interval is not None and now - readings[0][0] > max(SILENT_FACTOR * interval, SILENT_MIN_MSECS)

def getReadingStatsMany(sensorIds):
	infos = runPerSensor(sensorIds, lambda pipe, key: pipe.info(key))
	stats = {}
	for sensorId, info in infos.items():
		stats[sensorId] = {
			'memory': info.memory_usage if info else 0,
			'count': info.total_samples if info else 0,
			'retention': int(info.retention_msecs / 1000) if info else 0
			#'lastTimestamp': info.last_time_stamp,
			#'firstTimestamp': info.first_time_stamp
		}
	return stats

def getReadingStats(sensorId):
	return getReadingStatsMany([sensorId])[sensorId]
