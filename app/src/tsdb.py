import os
import redis

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')

READINGS_TOPIC = 'sensor-readings-topic'
READINGS_KEY_PREFIX = 'sensor-readings:'

redisDb = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
ts = redisDb.ts()

def readingsKey(sensorId):
	return READINGS_KEY_PREFIX + str(sensorId)

def sensorIdFromKey(key):
	suffix = key[len(READINGS_KEY_PREFIX):]
	return int(suffix) if key.startswith(READINGS_KEY_PREFIX) and suffix.isdigit() else None

def isMissingKeyError(e):
	return isinstance(e, redis.ResponseError) and 'key does not exist' in str(e)

def createSeries(sensorId, retentionMsecs):
	"""Create the sensor's time series, or align its retention if it already exists."""
	key = readingsKey(sensorId)
	try:
		ts.create(key, retention_msecs=retentionMsecs)
	except redis.ResponseError as e:
		if 'key already exists' not in str(e):
			raise
		ts.alter(key, retention_msecs=retentionMsecs)

def deleteSeries(sensorIds):
	keys = [readingsKey(sensorId) for sensorId in sensorIds]
	if keys:
		redisDb.delete(*keys)

def findSeriesSensorIds():
	sensorIds = set()
	for key in redisDb.scan_iter(match=READINGS_KEY_PREFIX + '*', count=1000):
		sensorId = sensorIdFromKey(key)
		if sensorId is not None:
			sensorIds.add(sensorId)
	return sensorIds

def mergeSeries(fromSensorId, toSensorId):
	"""Copy all readings to another sensor's series and delete the source, unless some could not be copied."""
	fromKey = readingsKey(fromSensorId)
	try:
		samples = ts.range(fromKey, '-', '+')
	except redis.ResponseError as e:
		if isMissingKeyError(e):
			return (0, 0)
		raise

	toKey = readingsKey(toSensorId)
	failed = 0
	for i in range(0, len(samples), 1000):
		results = ts.madd([(toKey, timestamp, value) for timestamp, value in samples[i:i + 1000]])
		failed += sum(1 for result in results if isinstance(result, Exception))

	if not failed:
		redisDb.delete(fromKey)
	return (len(samples) - failed, failed)
