import os

import db

def setProperty(property, value):
	db.execute('INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = excluded.value', (property, str(value)))

def getProperty(property, defaultValue):
	row = db.queryOne('SELECT value FROM settings WHERE key = ?', (property,))
	if row and row['value']:
		return row['value']
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

def isLoginAllowed(isAdmin):
	"""Turning off non-admin login locks out non-admins completely: their passwords, their tokens, and MQTT."""
	return bool(isAdmin) or getAllowNonAdminLogin()

def getMqttUsername():
	return os.environ.get('MQTT_USERNAME', 'mqtt')

def getMqttPassword():
	return os.environ.get('MQTT_PASSWORD', 'mqtt123')
