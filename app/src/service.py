from flask_restx import abort

from db import db, Keys
import util

def findDataset(auth, datasetName):
	validName = util.verifyValidName(datasetName, fail=False)
	if validName:
		datasetId = db.get(Keys.getDatasetIdByName(datasetName))
		if datasetId:
			if db.sismember(Keys.getUserDatasetIds(auth['username']), datasetId):
				dataset = db.hgetall(Keys.getDatasetById(datasetId))
				return dataset

	abort(404, "Unknown dataset '" + datasetName + "'")

def getDatasetNodes(datasetId):
	nodeIds = db.smembers(Keys.getDatasetNodeIds(datasetId))
	nodes = []
	for nodeId in nodeIds:
		node = db.hgetall(Keys.getNodeById(nodeId))
		cNode = cleanObject(node, ['name', 'desc'])
		nodes.append(cNode)
	return nodes

def findNode(datasetId, nodeName):
	validName = util.verifyValidName(nodeName, fail=False)
	if validName:
		nodeId = db.get(Keys.getNodeIdByName(datasetId, nodeName))
		if nodeId:
			node = db.hgetall(Keys.getNodeById(nodeId))
			return node

	abort(404, "Unknown node '" + nodeName + "'")

def findSensor(nodeId, sensorName):
	validName = util.verifyValidName(sensorName, fail=False)
	if validName:
		sensorId = db.get(Keys.getSensorIdByName(nodeId, sensorName))
		if sensorId:
			sensor = db.hgetall(Keys.getSensorById(sensorId))
			return sensor

	abort(404, "Unknown sensor '" + sensorName + "'")

def cleanObject(obj, fieldsToKeep):
	newObj = {}
	for field in fieldsToKeep:
		if field in obj:
			newObj[field] = obj[field]
	return newObj
