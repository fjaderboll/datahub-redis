from flask_restx import abort

import db
import tsdb
from services import util, cleaner, settings_service, reading_service

def verifyValidSensorName(nodeId, sensorName):
	util.verifyValidName(sensorName, "Name")

	if db.queryOne('SELECT 1 FROM sensors WHERE node_id = ? AND name = ?', (nodeId, sensorName)):
		abort(400, "Sensor '" + sensorName + "' already exists")

def getSensorById(sensorId):
	return db.queryOne('SELECT * FROM sensors WHERE id = ?', (sensorId,))

def getSensorByName(nodeId, name):
	return db.queryOne('SELECT * FROM sensors WHERE node_id = ? AND name = ?', (nodeId, name))

def createSensor(nodeId, name, desc='', unit=''):
	with db.transaction():
		verifyValidSensorName(nodeId, name)
		cursor = db.execute('INSERT INTO sensors (node_id, name, description, unit) VALUES (?, ?, ?, ?)', (nodeId, name, desc or '', unit or ''))

	sensorId = cursor.lastrowid
	tsdb.createSeries(sensorId, settings_service.getReadingsRetention())
	return getSensorById(sensorId)

def getOrCreateSensor(nodeId, name):
	created = db.query('INSERT INTO sensors (node_id, name) VALUES (?, ?) ON CONFLICT (node_id, name) DO NOTHING RETURNING id', (nodeId, name))
	if created:
		tsdb.createSeries(created[0]['id'], settings_service.getReadingsRetention())
	return getSensorByName(nodeId, name)

def updateSensor(sensor, name=None, desc=None, unit=None):
	with db.transaction():
		if name is not None:
			verifyValidSensorName(sensor['node_id'], name)
			db.execute('UPDATE sensors SET name = ? WHERE id = ?', (name, sensor['id']))

		if desc is not None:
			db.execute('UPDATE sensors SET description = ? WHERE id = ?', (desc, sensor['id']))

		if unit is not None:
			db.execute('UPDATE sensors SET unit = ? WHERE id = ?', (unit, sensor['id']))

	return getSensorById(sensor['id'])

def deleteSensor(sensor):
	db.execute('DELETE FROM sensors WHERE id = ?', (sensor['id'],))
	tsdb.deleteSeries([sensor['id']])

def getNodeSensors(datasetName, node):
	sensors = db.query('SELECT * FROM sensors WHERE node_id = ? ORDER BY name', (node['id'],))
	lastReadings = reading_service.getLastReadings([sensor['id'] for sensor in sensors])
	for sensor in sensors:
		sensor['lastReading'] = cleaner.cleanReading(lastReadings[sensor['id']], datasetName, node['name'], sensor)
	return sensors
