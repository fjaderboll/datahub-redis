from db import db, ts, Keys
from services import cleaner
import dateutil.parser as dp
from datetime import datetime

def parseTime(time, defaultValue):
	if time:
		try:
			offset = int(time)
			return datetime.now().timestamp() + offset*1000
		except ValueError:
			return dp.parse(time).timestamp()
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
