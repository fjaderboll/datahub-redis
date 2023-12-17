import redis

db = redis.Redis(decode_responses=True)

class Keys():
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
		return 'dataset-node-ids:' + datasetId

	def getNodeIdByName(datasetId, nodeName):
		return 'dataset:' + str(datasetId) + ':node-name:' + nodeName

	def getNodeById(nodeId):
		return 'node:' + str(nodeId)

	# sensors
	def getNodeSensorIds(nodeId):
		return 'node-sensor-ids:' + nodeId

	def getSensorIdByName(nodeId, sensorName):
		return 'node:' + str(nodeId) + ':sensor-name:' + sensorName

	def getSensorById(sensorId):
		return 'sensor:' + str(sensorId)
