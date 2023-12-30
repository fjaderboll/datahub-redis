import os
import redis

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')

db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
ts = db.ts()

class Keys():
	# settings
	def getSettings():
		return 'settings'

	# tokens
	def getToken(token):
		return 'token:' + token

	def getUsers():
		return 'users'

	def getUser(username):
		return 'user:' + username

	# counters
	def getTokenIdCounter():
		return 'id-counter-token'

	def getDatasetIdCounter():
		return 'id-counter-dataset'

	def getNodeIdCounter():
		return 'id-counter-node'

	def getSensorIdCounter():
		return 'id-counter-sensor'

	# dataset
	def getUserDatasetIds(username):
		return 'user-dataset-ids:' + username

	def getDatasetIdByName(datasetName):
		return 'dataset-name:' + datasetName

	def getDatasetById(datasetId):
		return 'dataset:' + str(datasetId)

	# nodes
	def getDatasetNodeIds(datasetId):
		return 'dataset-node-ids:' + str(datasetId)

	def getNodeIdByName(datasetId, nodeName):
		return 'dataset-node-name:' + str(datasetId) + ':node-name:' + nodeName

	def getNodeById(nodeId):
		return 'node:' + str(nodeId)

	# sensors
	def getNodeSensorIds(nodeId):
		return 'node-sensor-ids:' + str(nodeId)

	def getSensorIdByName(nodeId, sensorName):
		return 'node-sensor-name:' + str(nodeId) + ':sensor-name:' + sensorName

	def getSensorById(sensorId):
		return 'sensor:' + str(sensorId)

	# readings
	def getReadings(sensorId):
		return 'sensor-readings:' + str(sensorId)

	def getReadingsTopic():
		return 'sensor-readings-topic'
