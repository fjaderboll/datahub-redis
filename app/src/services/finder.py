from flask_restx import abort

import db
from services import util, dataset_service, node_service, sensor_service

def findDataset(auth, datasetName, create=False, validateUser=True):
	validName = util.verifyValidName(datasetName, fail=False)
	if validName:
		if validateUser:
			dataset = dataset_service.findUserDataset(auth['username'], datasetName)
		else:
			dataset = db.queryOne('SELECT * FROM datasets WHERE name = ?', (datasetName,))

		if dataset:
			return dataset
		elif create and not validateUser:
			return dataset_service.createDataset(datasetName, auth['username'])

	abort(404, "Unknown dataset '" + datasetName + "'")

def findNode(datasetId, nodeName, create=False):
	validName = util.verifyValidName(nodeName, fail=False)
	if validName:
		if create:
			return node_service.getOrCreateNode(datasetId, nodeName)

		node = node_service.getNodeByName(datasetId, nodeName)
		if node:
			return node

	abort(404, "Unknown node '" + nodeName + "'")

def findSensor(nodeId, sensorName, create=False):
	validName = util.verifyValidName(sensorName, fail=False)
	if validName:
		if create:
			return sensor_service.getOrCreateSensor(nodeId, sensorName)

		sensor = sensor_service.getSensorByName(nodeId, sensorName)
		if sensor:
			return sensor

	abort(404, "Unknown sensor '" + sensorName + "'")
