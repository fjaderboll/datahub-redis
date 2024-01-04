from flask_restx import Resource, fields, abort

from db import db, Keys
from services import util, sensor_service

def verifyValidNodeName(datasetId, nodeName):
	util.verifyValidName(nodeName, "Name")

	nodeId = db.get(Keys.getNodeIdByName(datasetId, nodeName))
	if nodeId:
		abort(400, "Node '" + nodeName + "' already exists")

def createNode(datasetId, name, desc=''):
	verifyValidNodeName(datasetId, name)

	nodeId = db.incr(Keys.getNodeIdCounter())
	node = {
		'id': nodeId,
		'datasetId': datasetId,
		'name': name,
		'desc': desc
	}
	db.set(Keys.getNodeIdByName(datasetId, name), nodeId)
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

def getDatasetNodes(datasetId):
	nodeIds = db.smembers(Keys.getDatasetNodeIds(datasetId))
	nodes = []
	for nodeId in nodeIds:
		node = db.hgetall(Keys.getNodeById(nodeId))
		nodes.append(node)
	return nodes
