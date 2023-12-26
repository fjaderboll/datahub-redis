from flask_restx import Resource, fields, abort
from flask import request

from api import api, auth_required
from db import db, Keys
from util import NullableString
import service
from services import cleaner, reading_service

from endpoints.datasets_nodes_sensors import ns

@ns.route('/<string:datasetName>/nodes/<string:nodeName>/sensors/<string:sensorName>/readings')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
@ns.param('sensorName', 'Sensor name')
class ReadingsList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	@api.doc(params={
		'after':  {'in': 'query', 'description': 'Only return readings after this ISO timestamp or relative time in seconds', 'example': '-3600'},
		'before': {'in': 'query', 'description': 'Only return readings before this ISO timestamp or relative time in seconds', 'example': '2023-12-26T10:15:30+01:00'},
		'limit':  {'in': 'query', 'description': 'Limits the result to this number of readings', 'default': '1000'}
	})
	def get(auth, self, datasetName, nodeName, sensorName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		sensor = service.findSensor(node['id'], sensorName)

		after = request.args.get('after')
		before = request.args.get('before')
		limit = request.args.get('limit')

		readings = reading_service.getReadings(sensor['id'], after=after, before=before, limit=limit)
		return cleaner.cleanReadings(readings, dataset, node, sensor)

	createFields = api.model('CreateReadingData', {
		'value': fields.String(description='The value', required=True),
		'time': NullableString(description='An ISO timestamp or relative time in seconds', required=False)
	})

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect(createFields, validate=True)
	def post(auth, self, datasetName, nodeName, sensorName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		sensor = service.findSensor(node['id'], sensorName)

		input = api.payload
		value = input['value']
		time = input['time'] if 'time' in input else None

		reading = reading_service.createReading(sensor['id'], value, time=time)
		return cleaner.cleanReading(reading, dataset, node, sensor)
