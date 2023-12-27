from flask_restx import Resource

from api import api, auth_required
from db import db, Keys
from services import util, cleaner, finder, sensor_service, reading_service

from endpoints.datasets_nodes import ns

@ns.route('/<string:datasetName>/nodes/<string:nodeName>/sensors')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
class SensorsList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self, datasetName, nodeName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		sensors = sensor_service.getNodeSensors(node['id'], dataset, node)
		return cleaner.cleanSensors(sensors)

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	def post(auth, self, datasetName, nodeName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)

		input = api.payload
		name = input['name']
		desc = input['desc']
		unit = input['unit']

		sensor = sensor_service.createSensor(node['id'], name, desc, unit)
		return cleaner.cleanSensor(sensor)

@ns.route('/<string:datasetName>/nodes/<string:nodeName>/sensors/<string:sensorName>')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
@ns.param('sensorName', 'Sensor name')
class SensorsView(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown sensor')
	@auth_required
	def get(auth, self, datasetName, nodeName, sensorName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		sensor = finder.findSensor(node['id'], sensorName)
		sensor['lastReading'] = cleaner.cleanReading(reading_service.getLastReading(sensor['id']), dataset, node, sensor)
		sensor['readingStats'] = reading_service.getReadingStats(sensor['id'])

		return cleaner.cleanSensor(sensor)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown sensor')
	@auth_required
	def put(auth, self, datasetName, nodeName, sensorName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		sensor = finder.findSensor(node['id'], sensorName)

		sKey = Keys.getSensorById(sensor['id'])

		input = api.payload
		if 'name' in input:
			util.verifyValidName(input['name'], "Name")
			db.hset(sKey, 'name', input['name'])
			db.rename(Keys.getSensorIdByName(node['id'], sensorName), Keys.getSensorIdByName(node['id'], input['name']))

		if 'desc' in input:
			db.hset(sKey, 'desc', input['desc'])

		if 'unit' in input:
			db.hset(sKey, 'unit', input['unit'])

		sensor = db.hgetall(sKey)
		return cleaner.cleanSensor(sensor)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown sensor')
	@auth_required
	def delete(auth, self, datasetName, nodeName, sensorName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		sensor = finder.findSensor(node['id'], sensorName)

		sensor_service.deleteSensor(sensor['id'])

		return "Removed sensor '" + sensorName + "'"
