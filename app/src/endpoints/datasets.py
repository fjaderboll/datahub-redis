from flask_restx import Resource

from api import api, auth_required
from services import util, finder, cleaner, swagger_service, dataset_service, node_service, sensor_service, user_service

ns = api.namespace('datasets', description='List, view, create and delete datasets')

@ns.route('/')
class DatasetsList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		return cleaner.cleanDatasets(dataset_service.getUserDatasets(auth['username']))

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect(swagger_service.createDatasetData)
	def post(auth, self):
		name = util.getPayload('name')
		desc = util.getPayload('desc')

		dataset = dataset_service.createDataset(name, auth['username'], desc)
		return cleaner.cleanDataset(dataset)

@ns.route('/<string:datasetName>')
@ns.param('datasetName', 'Dataset name')
class DatasetsView(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def get(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)
		dataset['nodes'] = cleaner.cleanNodes(node_service.getDatasetNodes(dataset['id']))

		return cleaner.cleanDataset(dataset)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	@api.expect(swagger_service.updateDatasetData)
	def put(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)
		dataset = dataset_service.updateDataset(dataset, name=util.getPayload('name'), desc=util.getPayload('desc'))
		return cleaner.cleanDataset(dataset)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def delete(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)
		dataset_service.deleteDataset(dataset)
		return "Removed dataset '" + datasetName + "'"

@ns.route('/<string:datasetName>/users')
@ns.param('datasetName', 'Dataset name')
class DatasetsUsers(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def get(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)

		return dataset_service.findDatasetUsernames(dataset['id'])

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect(swagger_service.addDatasetUserData)
	def post(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)
		username = util.getPayload('username')
		user_service.findUser(username, statusCode=400)

		dataset_service.addDatasetUser(dataset['id'], username)
		return "Added user '" + username + "' to dataset"

@ns.route('/<string:datasetName>/users/<string:username>')
@ns.param('datasetName', 'Dataset name')
@ns.param('username', 'Username')
class DatasetsUsersUser(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def delete(auth, self, datasetName, username):
		dataset = finder.findDataset(auth, datasetName)
		user_service.findUser(username)

		dataset_service.removeDatasetUser(dataset['id'], username)
		return "Removed user '" + username + "' from dataset"

@ns.route('/<string:datasetName>/units')
@ns.param('datasetName', 'Dataset name')
class DatasetsUnits(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def get(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)

		return sensor_service.getDatasetUnits(dataset['id'])
