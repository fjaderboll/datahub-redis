from flask_restx import Resource

from api import api, auth_required
from services import swagger_service, reading_service

from endpoints.datasets_nodes_sensors import ns

@ns.route('/<string:datasetName>/nodes/<string:nodeName>/sensors/<string:sensorName>/readings')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
@ns.param('sensorName', 'Sensor name')
class SensorReadingsList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	@api.doc(params=swagger_service.getReadingsParams)
	def get(auth, self, datasetName, nodeName, sensorName):
		return reading_service.getReadings(auth, datasetName, nodeName, sensorName)

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect([swagger_service.createSensorReadingData])
	def post(auth, self, datasetName, nodeName, sensorName):
		return reading_service.createReadings(auth, datasetName, nodeName, sensorName)

	@ns.response(200, 'Success')
	@auth_required
	@api.doc(params=swagger_service.deleteReadingsParams)
	def delete(auth, self, datasetName, nodeName, sensorName):
		return reading_service.deleteReadings(auth, datasetName, nodeName, sensorName)

@ns.route('/<string:datasetName>/nodes/<string:nodeName>/readings')
@ns.param('datasetName', 'Dataset name')
@ns.param('nodeName', 'Node name')
class NodeReadingsList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	@api.doc(params=swagger_service.getReadingsParams)
	def get(auth, self, datasetName, nodeName):
		return reading_service.getReadings(auth, datasetName, nodeName, None)

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect([swagger_service.createNodeReadingData])
	def post(auth, self, datasetName, nodeName):
		return reading_service.createReadings(auth, datasetName, nodeName, None)

	@ns.response(200, 'Success')
	@auth_required
	@api.doc(params=swagger_service.deleteReadingsParams)
	def delete(auth, self, datasetName, nodeName):
		return reading_service.deleteReadings(auth, datasetName, nodeName, None)

@ns.route('/<string:datasetName>/readings')
@ns.param('datasetName', 'Dataset name')
class DatasetReadingsList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	@api.doc(params=swagger_service.getReadingsParams)
	def get(auth, self, datasetName):
		return reading_service.getReadings(auth, datasetName, None, None)

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect([swagger_service.createDatasetReadingData])
	def post(auth, self, datasetName):
		return reading_service.createReadings(auth, datasetName, None, None)

	@ns.response(200, 'Success')
	@auth_required
	@api.doc(params=swagger_service.deleteReadingsParams)
	def delete(auth, self, datasetName):
		return reading_service.deleteReadings(auth, datasetName, None, None)
