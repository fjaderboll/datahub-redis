from flask_restx import Resource, fields, abort
from db import db, ts, Keys
from services import cleaner, settings_service, reading_service
import dateutil.parser as dp
from datetime import datetime
import util

def createSensor(nodeId, name, desc=None, unit=None):
	util.verifyValidName(name, "Name")

	sensorIdKeyName = Keys.getSensorIdByName(nodeId, name)
	sensorId = db.get(sensorIdKeyName)
	if sensorId:
		abort(400, "Sensor '" + name + "' already exists")

	sensorId = db.incr(Keys.getSensorIdCounter())
	sensor = {
		'id': sensorId,
		'name': name,
		'desc': desc,
		'unit': unit
	}
	db.set(sensorIdKeyName, sensorId)
	db.hset(Keys.getSensorById(sensorId), mapping=sensor)
	db.sadd(Keys.getNodeSensorIds(nodeId), sensorId)
	ts.create(Keys.getReadings(sensorId), retention_msecs=settings_service.getReadingsRetention())

	return sensor

def getNodeSensors(nodeId, dataset, node):
	sensorIds = db.smembers(Keys.getNodeSensorIds(nodeId))
	sensors = []
	for sensorId in sensorIds:
		sensor = db.hgetall(Keys.getSensorById(sensorId))
		sensor['lastReading'] = cleaner.cleanReading(reading_service.getLastReading(sensor['id']), dataset, node, sensor)
		sensors.append(sensor)
	return sensors
