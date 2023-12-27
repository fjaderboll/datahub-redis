from flask_restx import abort

from db import db, Keys
from services import util

def findDataset(auth, datasetName, create=False):
	validName = util.verifyValidName(datasetName, fail=False)
	if validName:
		datasetId = db.get(Keys.getDatasetIdByName(datasetName))
		if datasetId:
			if db.sismember(Keys.getUserDatasetIds(auth['username']), datasetId):
				dataset = db.hgetall(Keys.getDatasetById(datasetId))
				return dataset
		elif create:
			pass # TODO

	abort(404, "Unknown dataset '" + datasetName + "'")

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
