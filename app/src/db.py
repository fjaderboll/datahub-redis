import redis

db = redis.Redis(decode_responses=True)

class Keys():
	def getToken(token):
		return 'token:' + token

	def getUsers():
		return 'users'

	def getUser(username):
		return 'user:' + username

	def getTokenIdCounter():
		return 'id-counter-token'

	def getDatasetIdCounter():
		return 'id-counter-dataset'

	def getDatasets():
		return 'datasets'

	def getUserDatasetIds(username):
		return 'user-dataset-ids:' + username

	def getDatasetByName(datasetName):
		return 'dataset-name:' + datasetName

	def getDatasetById(datasetId):
		return 'dataset-id:' + str(datasetId)

	def getDatasetNodes(dataset):
		return 'dataset-nodes:' + dataset

	def getNode(dataset, node):
		return 'dataset:' + dataset + ':node:' + node

	def getNodeSensors(dataset, node):
		return 'dataset:' + dataset + ':node-sensors:' + node

	def getSensor(dataset, node, sensor):
		return 'dataset:' + dataset + ':node:' + node + ':' + sensor
