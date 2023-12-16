from flask_restx import Resource, fields, abort

from api import api, auth_required
from db import db, Keys
import util
import service

from endpoints.datasets import ns

@ns.route('/<string:datasetName>/nodes')
@ns.param('datasetName', 'Dataset name')
class NodesList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self, datasetName):
		dataset = service.findDataset(auth, datasetName)
		return service.getDatasetNodes(dataset['id'])

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	def post(auth, self, datasetName):
		dataset = service.findDataset(auth, datasetName)

		input = api.payload
		name = input['name']
		desc = input['desc']

		util.verifyValidName(input['name'], "Name")

		nodeKeyName = Keys.getDatasetByName(input['name'])
		nodeId = db.get(nodeKeyName)
		if nodeId:
			abort(400, "Node '" + name + "' already exists")

		nodeId = db.incr(Keys.getNodeIdCounter())
		node = {
			'id': nodeId,
			'name': name,
			'desc': desc
		}
		db.set(nodeKeyName, nodeId)
		db.hset(Keys.getNodeById(nodeId), mapping=node)
		db.sadd(Keys.getDatasetNodeIds(dataset['id']), nodeId)

		return service.cleanObject(node, ['name', 'desc'])

@ns.route('/<string:datasetName>/nodes/<string:nodeName>')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
class NodesView(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def get(auth, self, datasetName):
		return service.findDataset(auth, datasetName)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def put(auth, self, datasetName):
		dataset = service.findDataset(auth, datasetName)
		dKey = Keys.getDatasetById(dataset['id'])

		input = api.payload
		if 'name' in input:
			db.hset(dKey, 'name', input['name'])
			db.rename(Keys.getDatasetByName(datasetName), Keys.getDatasetByName(input['name']))

		if 'desc' in input:
			db.hset(dKey, 'desc', input['desc'])

		dataset = db.hgetall(dKey)
		dataset = service.cleanObject(dataset, ['name', 'desc'])
		return dataset

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def delete(auth, self, datasetName):
		dataset = service.findDataset(auth, datasetName)

		for username in db.smembers(Keys.getUsers()):
			db.srem(Keys.getUserDatasetIds(username), dataset['id'])
		db.delete(Keys.getDatasetByName(datasetName))
		db.delete(Keys.getDatasetById(dataset['id']))

		# TODO remove nodes/sensors/readings/tokens/exports

		return "Removed dataset '" + datasetName + "'"
