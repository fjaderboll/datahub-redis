from flask_restx import abort

from db import db, ts, Keys
from services import util, node_service

def createDataset(name, username, desc=''):
	util.verifyValidName(name, "Name")

	datasetKeyName = Keys.getDatasetIdByName(name)
	datasetId = db.get(datasetKeyName)
	if datasetId:
		abort(400, "Dataset '" + name + "' already exists")

	datasetId = db.incr(Keys.getDatasetIdCounter())
	dataset = {
		'id': datasetId,
		'name': name,
		'desc': desc
	}
	db.set(datasetKeyName, datasetId)
	db.hset(Keys.getDatasetById(datasetId), mapping=dataset)
	db.sadd(Keys.getUserDatasetIds(username), datasetId)

	return dataset

def deleteDataset(dataset):
	nodeIds = db.smembers(Keys.getDatasetNodeIds(dataset['id']))
	for nodeId in nodeIds:
		node_service.deleteNode(nodeId)

	for username in db.smembers(Keys.getUsers()):
		db.srem(Keys.getUserDatasetIds(username), dataset['id'])
	db.delete(Keys.getDatasetIdByName(dataset['name']))
	db.delete(Keys.getDatasetById(dataset['id']))
	db.delete(Keys.getDatasetNodeIds(dataset['id']))
