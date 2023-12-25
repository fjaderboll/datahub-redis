from flask_restx import Resource, fields, abort

from api import api, auth_required
from db import db, Keys
import util
import service
from services import cleaner

from endpoints.datasets_nodes import ns

@ns.route('/<string:datasetName>/nodes/<string:nodeName>/sensors')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
class SensorsList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self, datasetName, nodeName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		return service.getNodeSensors(node['id'])

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	def post(auth, self, datasetName, nodeName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)

		input = api.payload
		name = input['name']
		desc = input['desc']
		unit = input['unit']

		util.verifyValidName(name, "Name")

		sensorIdKeyName = Keys.getSensorIdByName(node['id'], name)
		sensorId = db.get(sensorIdKeyName)
		if sensorId:
			abort(400, "Sensor '" + name + "' already exists")

		sensorId = db.incr(Keys.getSensorIdCounter())
		sensor = {
			'id': sensorId,
			'name': name,
			'desc': desc,
			'unit': unit
		}
		db.set(sensorIdKeyName, sensorId)
		db.hset(Keys.getSensorById(sensorId), mapping=sensor)
		db.sadd(Keys.getNodeSensorIds(node['id']), sensorId)

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
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		sensor = service.findSensor(node['id'], sensorName)

		return cleaner.cleanSensor(sensor)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown sensor')
	@auth_required
	def put(auth, self, datasetName, nodeName, sensorName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		sensor = service.findSensor(node['id'], sensorName)

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
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		sensor = service.findSensor(node['id'], sensorName)

		db.srem(Keys.getNodeSensorIds(node['id']), sensor['id'])
		db.delete(Keys.getSensorIdByName(node['id'], sensorName))
		db.delete(Keys.getSensorById(sensor['id']))

		# TODO remove readings

		return "Removed sensor '" + sensorName + "'"
