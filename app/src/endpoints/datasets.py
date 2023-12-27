from flask_restx import Resource

from api import api, auth_required
from db import db, Keys
from services import util, finder, cleaner, dataset_service, node_service

ns = api.namespace('datasets', description='List, view, create and delete datasets')

@ns.route('/')
class DatasetsList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		datasetIds = db.smembers(Keys.getUserDatasetIds(auth['username']))
		datasets = []
		for datasetId in datasetIds:
			dataset = db.hgetall(Keys.getDatasetById(datasetId))
			datasets.append(dataset)
		return cleaner.cleanDatasets(datasets)

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	def post(auth, self):
		input = api.payload
		name = input['name']
		desc = input['desc']

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
	def put(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)
		dKey = Keys.getDatasetById(dataset['id'])

		input = api.payload
		if 'name' in input:
			util.verifyValidName(input['name'], "Name")
			db.hset(dKey, 'name', input['name'])
			db.rename(Keys.getDatasetIdByName(datasetName), Keys.getDatasetIdByName(input['name']))

		if 'desc' in input:
			db.hset(dKey, 'desc', input['desc'])

		dataset = db.hgetall(dKey)
		return cleaner.cleanDataset(dataset)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def delete(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)
		dataset_service.deleteDataset(dataset)
		return "Removed dataset '" + datasetName + "'"
