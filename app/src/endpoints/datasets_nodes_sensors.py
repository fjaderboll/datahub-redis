from flask_restx import Resource

from api import api, auth_required
from services import util, cleaner, finder, swagger_service, sensor_service, reading_service

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
		sensors = sensor_service.getNodeSensors(dataset['name'], node)
		return cleaner.cleanSensors(sensors)

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect(swagger_service.createSensorData)
	def post(auth, self, datasetName, nodeName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)

		name = util.getPayload('name')
		desc = util.getPayload('desc')
		unit = util.getPayload('unit')

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
		sensor['lastReading'] = cleaner.cleanReading(reading_service.getLastReadings([sensor['id']])[sensor['id']], dataset['name'], node['name'], sensor)
		sensor['readingStats'] = reading_service.getReadingStats(sensor['id'])

		return cleaner.cleanSensor(sensor)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown sensor')
	@auth_required
	@api.expect(swagger_service.updateSensorData)
	def put(auth, self, datasetName, nodeName, sensorName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		sensor = finder.findSensor(node['id'], sensorName)
		sensor = sensor_service.updateSensor(sensor, name=util.getPayload('name'), desc=util.getPayload('desc'), unit=util.getPayload('unit'))
		return cleaner.cleanSensor(sensor)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown sensor')
	@auth_required
	def delete(auth, self, datasetName, nodeName, sensorName):
		dataset = finder.findDataset(auth, datasetName)
		node = finder.findNode(dataset['id'], nodeName)
		sensor = finder.findSensor(node['id'], sensorName)

		sensor_service.deleteSensor(sensor)

		return "Removed sensor '" + sensorName + "'"
