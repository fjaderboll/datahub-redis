from db import db, ts, Keys
from services import cleaner
import dateutil.parser as dp
from datetime import datetime

def setProperty(property, value):
	db.hset(Keys.getSettings(), property, value)

def getProperty(property, defaultValue):
	value = db.hget(Keys.getSettings(), 'retention')
	if value:
		return value
	return defaultValue

def getReadingsRetention():
	return int(getProperty('retention', 1000 * 60 * 60 * 24 * 365)) # one year

def setReadingsRetention(retention):
	setProperty('retention', retention)

def getTokenTTL():
	return int(getProperty('token-ttl', 3600))

def setTokenTTL(ttl):
	setProperty('token-ttl', ttl)
