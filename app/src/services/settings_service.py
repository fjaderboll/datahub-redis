from db import db, Keys

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
