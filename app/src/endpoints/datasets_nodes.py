from flask_restx import Resource

from api import api, auth_required
from services import util, finder, cleaner, swagger_service, node_service, sensor_service

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
	@api.expect(swagger_service.createNodeData)
	def post(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)

		name = util.getPayload('name')
		desc = util.getPayload('desc')

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

		sensors = sensor_service.getNodeSensors(dataset['name'], node)
		node['sensors'] = cleaner.cleanSensors(sensors)

		return cleaner.cleanNode(node)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown node')
	@auth_required
	@api.expect(swagger_service.updateNodeData)
	def put(auth, self, datasetName, nodeName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		node = node_service.updateNode(node, name=util.getPayload('name'), desc=util.getPayload('desc'))
		return cleaner.cleanNode(node)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown node')
	@auth_required
	def delete(auth, self, datasetName, nodeName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)

		node_service.deleteNode(node)

		return "Removed node '" + nodeName + "'"
