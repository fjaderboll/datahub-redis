from flask_restx import abort

from db import db, ts, Keys
from services import util, cleaner, settings_service, reading_service

def createSensor(nodeId, name, desc='', unit=''):
	util.verifyValidName(name, "Name")

	sensorIdKeyName = Keys.getSensorIdByName(nodeId, name)
	sensorId = db.get(sensorIdKeyName)
	if sensorId:
		abort(400, "Sensor '" + name + "' already exists")

	sensorId = db.incr(Keys.getSensorIdCounter())
	sensor = {
		'id': sensorId,
		'nodeId': nodeId,
		'name': name,
		'desc': desc,
		'unit': unit
	}
	db.set(sensorIdKeyName, sensorId)
	db.hset(Keys.getSensorById(sensorId), mapping=sensor)
	db.sadd(Keys.getNodeSensorIds(nodeId), sensorId)
	ts.create(Keys.getReadings(sensorId), retention_msecs=settings_service.getReadingsRetention())

	return sensor

def deleteSensor(sensorId):
	sensor = db.hgetall(Keys.getSensorById(sensorId))

	#reading_service.deleteReadings(sensor['id']) # not needed as we delete the entire time serie
	db.delete(Keys.getReadings(sensor['id']))

	db.srem(Keys.getNodeSensorIds(sensor['nodeId']), sensor['id'])
	db.delete(Keys.getSensorIdByName(sensor['nodeId'], sensor['name']))
	db.delete(Keys.getSensorById(sensor['id']))

def getNodeSensors(nodeId, dataset, node):
	sensorIds = db.smembers(Keys.getNodeSensorIds(nodeId))
	sensors = []
	for sensorId in sensorIds:
		sensor = db.hgetall(Keys.getSensorById(sensorId))
		sensor['lastReading'] = cleaner.cleanReading(reading_service.getLastReading(sensor['id']), dataset, node, sensor)
		sensors.append(sensor)
	return sensors
