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
		name = util.getInput('name')
		desc = util.getInput('desc')

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

		name = util.getInput('name')
		desc = util.getInput('desc')

		if name:
			util.verifyValidName(name, "Name")
			db.hset(dKey, 'name', name)
			db.rename(Keys.getDatasetIdByName(datasetName), Keys.getDatasetIdByName(name))

		if desc:
			db.hset(dKey, 'desc', desc)

		dataset = db.hgetall(dKey)
		return cleaner.cleanDataset(dataset)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def delete(auth, self, datasetName):
		dataset = finder.findDataset(auth, datasetName)
		dataset_service.deleteDataset(dataset)
		return "Removed dataset '" + datasetName + "'"
