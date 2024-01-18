from db import db, Keys

def setProperty(property, value):
	db.hset(Keys.getSettings(), property, value)

def getProperty(property, defaultValue):
	value = db.hget(Keys.getSettings(), property)
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

def getAllowPublicCreateUser():
	return bool(int(getProperty('allow-public-create-user', True)))

def setAllowPublicCreateUser(allow):
	setProperty('allow-public-create-user', int(allow))

def getAllowNonAdminLogin():
	return bool(int(getProperty('allow-non-admin-login', True)))

def setAllowNonAdminLogin(allow):
	setProperty('allow-non-admin-login', int(allow))
