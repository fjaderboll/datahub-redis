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

def isDuplicateError(e):
	"""A sample already exists at that timestamp (the default DUPLICATE_POLICY is BLOCK)."""
	return isinstance(e, redis.ResponseError) and 'DUPLICATE_POLICY' in str(e)

# A time series holds one sample per millisecond. This adds the sample at the given timestamp or,
# if taken, the first free millisecond after it. As a script it runs atomically, so concurrent
# requests (also from other workers) can't take the same free millisecond in between.
_addAtFreeTimestamp = redisDb.register_script('''
local key, ts, value = KEYS[1], tonumber(ARGV[1]), ARGV[2]
for attempt = 1, 100 do
	local result = redis.pcall('TS.ADD', key, string.format('%d', ts), value)
	if type(result) ~= 'table' or not result.err or not string.find(result.err, 'DUPLICATE_POLICY', 1, true) then
		return result
	end
	for _, sample in ipairs(redis.call('TS.RANGE', key, string.format('%d', ts), string.format('%d', ts + 1000))) do
		if tonumber(sample[1]) ~= ts then
			break
		end
		ts = ts + 1
	end
end
return redis.error_reply('No free timestamp found')
''')

def addAtFreeTimestamp(key, timestamp, value):
	"""Add a sample at 'timestamp' or the first free millisecond after it, returns the timestamp used."""
	return _addAtFreeTimestamp(keys=[key], args=[timestamp, value])

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
