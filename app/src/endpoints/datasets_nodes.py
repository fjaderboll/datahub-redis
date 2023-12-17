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

		nodeIdKeyName = Keys.getNodeIdByName(dataset['id'], input['name'])
		nodeId = db.get(nodeIdKeyName)
		if nodeId:
			abort(400, "Node '" + name + "' already exists")

		nodeId = db.incr(Keys.getNodeIdCounter())
		node = {
			'id': nodeId,
			'name': name,
			'desc': desc
		}
		db.set(nodeIdKeyName, nodeId)
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
	def get(auth, self, datasetName, nodeName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		node['sensors'] = None # service.getDatasetNodes(dataset['id'])

		return service.cleanObject(node, ['name', 'desc', 'sensors'])

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def put(auth, self, datasetName, nodeName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		nKey = Keys.getNodeById(node['id'])

		input = api.payload
		if 'name' in input:
			util.verifyValidName(input['name'], "Name")
			db.hset(nKey, 'name', input['name'])
			db.rename(Keys.getNodeIdByName(dataset['id'], nodeName), Keys.getNodeIdByName(dataset['id'], input['name']))

		if 'desc' in input:
			db.hset(nKey, 'desc', input['desc'])

		node = db.hgetall(nKey)
		node = service.cleanObject(node, ['name', 'desc'])
		return node

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def delete(auth, self, datasetName, nodeName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)

		db.srem(Keys.getDatasetNodeIds(dataset['id']), node['id'])
		db.delete(Keys.getNodeIdByName(dataset['id'], nodeName))
		db.delete(Keys.getNodeById(node['id']))

		# TODO remove sensors/readings

		return "Removed node '" + nodeName + "'"
