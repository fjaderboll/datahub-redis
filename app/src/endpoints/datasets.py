from flask_restx import Resource, fields, abort

from api import api, auth_required
from db import db, Keys
import util
import service

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
			dataset = service.cleanObject(dataset, ['name', 'desc'])
			datasets.append(dataset)
		return datasets

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	def post(auth, self):
		input = api.payload
		name = input['name']
		desc = input['desc']

		util.verifyValidName(input['name'], "Name")

		datasetKeyName = Keys.getDatasetIdByName(input['name'])
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
		db.sadd(Keys.getUserDatasetIds(auth['username']), datasetId)

		return service.cleanObject(dataset, ['name', 'desc'])

@ns.route('/<string:datasetName>')
@ns.param('datasetName', 'Dataset name')
class DatasetsView(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def get(auth, self, datasetName):
		dataset = service.findDataset(auth, datasetName)
		dataset['nodes'] = service.getDatasetNodes(dataset['id'])

		return service.cleanObject(dataset, ['name', 'desc', 'nodes'])

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def put(auth, self, datasetName):
		dataset = service.findDataset(auth, datasetName)
		dKey = Keys.getDatasetById(dataset['id'])

		input = api.payload
		if 'name' in input:
			util.verifyValidName(input['name'], "Name")
			db.hset(dKey, 'name', input['name'])
			db.rename(Keys.getDatasetIdByName(datasetName), Keys.getDatasetIdByName(input['name']))

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
		db.delete(Keys.getDatasetIdByName(datasetName))
		db.delete(Keys.getDatasetById(dataset['id']))

		# TODO remove nodes/sensors/readings

		return "Removed dataset '" + datasetName + "'"
