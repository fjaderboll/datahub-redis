from flask_restx import Resource, fields, abort

from api import api, auth_required
from db import db, Keys
import util
import service

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

		util.verifyValidName(name, "Name")

		sensorIdKeyName = Keys.getSensorIdByName(node['id'], name)
		sensorId = db.get(sensorIdKeyName)
		if sensorId:
			abort(400, "Sensor '" + name + "' already exists")

		sensorId = db.incr(Keys.getSensorIdCounter())
		sensor = {
			'id': sensorId,
			'name': name,
			'desc': desc
		}
		db.set(sensorIdKeyName, sensorId)
		db.hset(Keys.getSensorById(sensorId), mapping=sensor)
		db.sadd(Keys.getNodeSensorIds(node['id']), sensorId)

		return service.cleanObject(sensor, ['name', 'desc'])

@ns.route('/<string:datasetName>/nodes/<string:nodeName>/sensors/<string:sensorName>')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
@ns.param('sensorName', 'Sensor name')
class SensorsView(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown sensor')
	@auth_required
	def get(auth, self, datasetName, nodeName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		node['sensors'] = None # service.getDatasetNodes(dataset['id'])

		return service.cleanObject(node, ['name', 'desc', 'sensors'])

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown sensor')
	@auth_required
	def put(auth, self, datasetName, nodeName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)
		nKey = Keys.getNodeById(node['id'])

		input = api.payload
		if 'name' in input:
			util.verifyValidName(input['name'], "Name")
			db.hset(nKey, 'name', input['name'])
			db.rename(Keys.getNodeIdByName(dataset['id'], nodeName), Keys.getNodeIdByName(dataset['id'], input['name']))

		if 'desc' in input:
			db.hset(nKey, 'desc', input['desc'])

		node = db.hgetall(nKey)
		node = service.cleanObject(node, ['name', 'desc'])
		return node

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown sensor')
	@auth_required
	def delete(auth, self, datasetName, nodeName):
		dataset = service.findDataset(auth, datasetName)
		node = service.findNode(dataset['id'], nodeName)

		db.srem(Keys.getDatasetNodeIds(dataset['id']), node['id'])
		db.delete(Keys.getNodeIdByName(dataset['id'], nodeName))
		db.delete(Keys.getNodeById(node['id']))

		# TODO remove sensors/readings

		return "Removed node '" + nodeName + "'"
