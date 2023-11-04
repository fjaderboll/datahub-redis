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
		util.verifyAdmin(auth)

		datasetNames = db.smembers(Keys.getUserDatasets(auth['username']))
		datasets = []
		for datasetName in datasetNames:
			dataset = db.hgetall(Keys.getDataset(datasetName))
			datasets.append(dataset)
		return datasets

	@api.doc(security=None)
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	def post(auth, self):
		input = api.payload
		name = input['name']
		desc = input['desc']

		util.verifyValidName(input['name'], "Name")

		dKey = Keys.getDataset(name)
		if db.exists(dKey):
			abort(400, "Dataset '" + name + "' already exists")

		dataset = {
			'name': name,
			'desc': desc
		}
		db.hset(dKey, mapping=dataset)
		db.sadd(Keys.getUserDatasets(auth['username']), name)
		return dataset

@ns.route('/<string:datasetName>')
@ns.param('datasetName', 'Dataset name')
class DatasetsView(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def get(auth, self, datasetName):
		return service.findDataset(auth, datasetName)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def put(auth, self, datasetName):
		service.findDataset(auth, datasetName)

		input = api.payload
		#if 'name' in input:
		#	db.srem(Keys.getUserDatasets(auth['username']), datasetName)
		#	db.sadd(Keys.getUserDatasets(auth['username']), input['name'])
		#	db.hset(Keys.getDataset(datasetName), 'name', input['name'])
		#	db.rename(Keys.getDataset(datasetName), Keys.getDataset(input['name']))
		#	datasetName = input['name']

		if 'desc' in input:
			db.hset(Keys.getDataset(datasetName), 'desc', input['desc'])

		return service.findDataset(auth, datasetName)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown dataset')
	@auth_required
	def delete(auth, self, datasetName):
		service.findDataset(auth, datasetName)

		for username in db.smembers(Keys.getUsers()):
			db.srem(Keys.getUserDatasets(username), datasetName)
		db.delete(Keys.getDataset(datasetName))

		# TODO remove nodes/sensors/readings/tokens/exports

		return "Removed dataset '" + datasetName + "'"
