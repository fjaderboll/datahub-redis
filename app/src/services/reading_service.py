from db import ts, Keys
import dateutil.parser as dp
from datetime import datetime

def parseTime(time, defaultValue):
	if time:
		try:
			offset = int(time)
			return int(datetime.now().timestamp()*1000 + offset*1000)
		except ValueError:
			return int(dp.parse(time).timestamp()*1000)
	return defaultValue

def createReading(sensorId, value, time=None):
	timestamp = parseTime(time, '*')

	key = Keys.getReadings(sensorId)
	ts.add(key, timestamp, value)
	return ts.get(key)

def getReadings(sensorId, after=None, before=None, limit=None):
	fromTime = parseTime(after, '-')
	toTime = parseTime(before, '+')
	count = int(limit)

	items = ts.range(Keys.getReadings(sensorId), fromTime, toTime, count=count)
	return items

def deleteReadings(sensorId, after=None, before=None):
	fromTime = parseTime(after, '-')
	toTime = parseTime(before, '+')

	return ts.delete(Keys.getReadings(sensorId), fromTime, toTime)

def getLastReading(sensorId):
	return ts.get(Keys.getReadings(sensorId))
