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

def guessUnit(nodeId, name):
	"""The unit most used by sensors with the same name in the node's dataset, '' if there are none."""
	row = db.queryOne('''
		SELECT s.unit FROM sensors s
		JOIN nodes n ON n.id = s.node_id
		WHERE n.dataset_id = (SELECT dataset_id FROM nodes WHERE id = ?) AND s.name = ? AND s.unit != ''
		GROUP BY s.unit
		ORDER BY COUNT(*) DESC, s.unit
		LIMIT 1
	''', (nodeId, name))
	return row['unit'] if row else ''

def getDatasetUnits(datasetId):
	rows = db.query('''
		SELECT DISTINCT s.unit FROM sensors s
		JOIN nodes n ON n.id = s.node_id
		WHERE n.dataset_id = ? AND s.unit != ''
		ORDER BY s.unit COLLATE NOCASE
	''', (datasetId,))
	return [row['unit'] for row in rows]

def createSensor(nodeId, name, desc='', unit=''):
	with db.transaction():
		verifyValidSensorName(nodeId, name)
		cursor = db.execute('INSERT INTO sensors (node_id, name, description, unit) VALUES (?, ?, ?, ?)', (nodeId, name, desc or '', unit or guessUnit(nodeId, name)))

	sensorId = cursor.lastrowid
	tsdb.createSeries(sensorId, settings_service.getReadingsRetention())
	return getSensorById(sensorId)

def getOrCreateSensor(nodeId, name):
	# looked up first, so readings for existing sensors don't take the database's write lock
	sensor = getSensorByName(nodeId, name)
	if sensor:
		return sensor

	created = db.query('INSERT INTO sensors (node_id, name, unit) VALUES (?, ?, ?) ON CONFLICT (node_id, name) DO NOTHING RETURNING id', (nodeId, name, guessUnit(nodeId, name)))
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
