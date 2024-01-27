from flask_restx import Resource
from flask import request

from api import api, auth_required
from services import cleaner, finder, swagger_service, reading_service

from endpoints.datasets_nodes_sensors import ns

@ns.route('/<string:datasetName>/nodes/<string:nodeName>/sensors/<string:sensorName>/readings')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
@ns.param('sensorName', 'Sensor name')
class SensorReadingsList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	@api.doc(params={
		'after':  {'in': 'query', 'description': 'Only return readings after this ISO timestamp or relative time in seconds', 'example': '-3600'},
		'before': {'in': 'query', 'description': 'Only return readings before this ISO timestamp or relative time in seconds', 'example': '2023-12-26T10:15:30+01:00'},
		'limit':  {'in': 'query', 'description': 'Limits the result to this number of readings', 'default': '1000'}
	})
	def get(auth, self, datasetName, nodeName, sensorName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		sensor = finder.findSensor(node['id'], sensorName)

		after = request.args.get('after')
		before = request.args.get('before')
		limit = request.args.get('limit')

		readings = reading_service.getReadings(sensor['id'], after=after, before=before, limit=limit)
		return cleaner.cleanReadings(readings, dataset, node, sensor)

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect([swagger_service.createSensorReadingData])
	def post(auth, self, datasetName, nodeName, sensorName):
		return reading_service.createReadings(auth, datasetName, nodeName, sensorName)

	@ns.response(200, 'Success')
	@auth_required
	@api.doc(params={
		'after':  {'in': 'query', 'description': 'Only delete readings after this ISO timestamp or relative time in seconds', 'example': '-3600'},
		'before': {'in': 'query', 'description': 'Only delete readings before this ISO timestamp or relative time in seconds', 'example': '2023-12-26T10:15:30+01:00'}
	})
	def delete(auth, self, datasetName, nodeName, sensorName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		sensor = finder.findSensor(node['id'], sensorName)

		after = request.args.get('after')
		before = request.args.get('before')

		n = reading_service.deleteReadings(sensor['id'], after=after, before=before)
		return "Removed " + str(n) + " readings"

@ns.route('/<string:datasetName>/nodes/<string:nodeName>/readings')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
class NodeReadingsList(Resource):
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect([swagger_service.createNodeReadingData])
	def post(auth, self, datasetName, nodeName):
		return reading_service.createReadings(auth, datasetName, nodeName, None)

@ns.route('/<string:datasetName>/readings')
@ns.param('datasetName', 'Dataset name')
class DatasetReadingsList(Resource):
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect([swagger_service.createDatasetReadingData])
	def post(auth, self, datasetName):
		return reading_service.createReadings(auth, datasetName, None, None)
