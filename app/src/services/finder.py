from flask_restx import abort

from db import db, Keys
from services import util, dataset_service, node_service, sensor_service

def findDataset(auth, datasetName, create=False):
	validName = util.verifyValidName(datasetName, fail=False)
	if validName:
		datasetId = db.get(Keys.getDatasetIdByName(datasetName))
		if datasetId:
			if db.sismember(Keys.getUserDatasetIds(auth['username']), datasetId):
				dataset = db.hgetall(Keys.getDatasetById(datasetId))
				return dataset
		elif create:
			return dataset_service.createDataset(datasetName, auth['username'])

	abort(404, "Unknown dataset '" + datasetName + "'")

def findNode(datasetId, nodeName, create=False):
	validName = util.verifyValidName(nodeName, fail=False)
	if validName:
		nodeId = db.get(Keys.getNodeIdByName(datasetId, nodeName))
		if nodeId:
			node = db.hgetall(Keys.getNodeById(nodeId))
			return node
		elif create:
			return node_service.createNode(datasetId, nodeName)

	abort(404, "Unknown node '" + nodeName + "'")

def findSensor(nodeId, sensorName, create=False):
	validName = util.verifyValidName(sensorName, fail=False)
	if validName:
		sensorId = db.get(Keys.getSensorIdByName(nodeId, sensorName))
		if sensorId:
			sensor = db.hgetall(Keys.getSensorById(sensorId))
			return sensor
		elif create:
			return sensor_service.createSensor(nodeId, sensorName)

	abort(404, "Unknown sensor '" + sensorName + "'")
