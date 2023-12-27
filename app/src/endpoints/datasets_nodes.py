from flask_restx import Resource

from api import api, auth_required
from db import db, Keys
from services import util, finder, cleaner, node_service, sensor_service

from endpoints.datasets import ns

@ns.route('/<string:datasetName>/nodes')
@ns.param('datasetName', 'Dataset name')
class NodesList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)
		return cleaner.cleanNodes(node_service.getDatasetNodes(dataset['id']))

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	def post(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)

		input = api.payload
		name = input['name']
		desc = input['desc']

		node = node_service.createNode(dataset['id'], name, desc)
		return cleaner.cleanNode(node)

@ns.route('/<string:datasetName>/nodes/<string:nodeName>')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
class NodesView(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown node')
	@auth_required
	def get(auth, self, datasetName, nodeName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)

		sensors = sensor_service.getNodeSensors(node['id'], dataset, node)
		node['sensors'] = cleaner.cleanSensors(sensors)

		return cleaner.cleanNode(node)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown node')
	@auth_required
	def put(auth, self, datasetName, nodeName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		nKey = Keys.getNodeById(node['id'])

		input = api.payload
		if 'name' in input:
			util.verifyValidName(input['name'], "Name")
			db.hset(nKey, 'name', input['name'])
			db.rename(Keys.getNodeIdByName(dataset['id'], nodeName), Keys.getNodeIdByName(dataset['id'], input['name']))

		if 'desc' in input:
			db.hset(nKey, 'desc', input['desc'])

		node = db.hgetall(nKey)
		node = cleaner.cleanNode(node)
		return node

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown node')
	@auth_required
	def delete(auth, self, datasetName, nodeName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)

		node_service.deleteNode(node['id'])

		return "Removed node '" + nodeName + "'"
