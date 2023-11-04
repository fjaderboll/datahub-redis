import redis

db = redis.Redis(decode_responses=True)

class Keys():
	def getToken(token):
		return 'token:' + token

	def getUsers():
		return 'users'

	def getUser(username):
		return 'user:' + username

	def getUserDatasets(username):
		return 'user-datasets:' + username

	def getDataset(dataset):
		return 'dataset:' + dataset

	def getDatasetNodes(dataset):
		return 'dataset-nodes:' + dataset

	def getNode(dataset, node):
		return 'dataset:' + dataset + ':node:' + node

	def getNodeSensors(dataset, node):
		return 'dataset:' + dataset + ':node-sensors:' + node

	def getSensor(dataset, node, sensor):
		return 'dataset:' + dataset + ':node:' + node + ':' + sensor
