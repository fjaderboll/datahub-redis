from flask_restx import Resource, fields, abort
from db import db, ts, Keys
from services import cleaner, settings_service, sensor_service
import dateutil.parser as dp
from datetime import datetime
import util

def createNode(datasetId, name, desc=None):
	util.verifyValidName(name, "Name")

	nodeIdKeyName = Keys.getNodeIdByName(datasetId, name)
	nodeId = db.get(nodeIdKeyName)
	if nodeId:
		abort(400, "Node '" + name + "' already exists")

	nodeId = db.incr(Keys.getNodeIdCounter())
	node = {
		'id': nodeId,
		'datasetId': datasetId,
		'name': name,
		'desc': desc
	}
	db.set(nodeIdKeyName, nodeId)
	db.hset(Keys.getNodeById(nodeId), mapping=node)
	db.sadd(Keys.getDatasetNodeIds(datasetId), nodeId)

	return node

def deleteNode(nodeId):
	node = db.hgetall(Keys.getNodeById(nodeId))

	sensorIds = db.smembers(Keys.getNodeSensorIds(node['id']))
	for sensorId in sensorIds:
		sensor_service.deleteSensor(sensorId)

	db.srem(Keys.getDatasetNodeIds(node['datasetId']), node['id'])
	db.delete(Keys.getNodeIdByName(node['datasetId'], node['name']))
	db.delete(Keys.getNodeById(node['id']))
	db.delete(Keys.getNodeSensorIds(node['id']))

