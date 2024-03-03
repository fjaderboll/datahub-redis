from flask_restx import Resource
from flask_restx import abort

import re

from api import api
from services import finder, swagger_service, settings_service, user_service

ns = api.namespace('mqtt', description='MQ broker endpoints')

@ns.route('/authenticate')
class Authenticate(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@api.expect(swagger_service.mqttAuthenticateData)
	def post(self):
		username = api.payload['username']
		password = api.payload['password']

		allow = False

		if username == settings_service.getMqttUsername():
			if password == settings_service.getMqttPassword():
				allow = True
		else:
			try:
				tokenInfo = user_service.login(username, password)
				allow = True
			except:
				pass

		return {
			"result": 'allow' if allow else 'ignore'
			#"is_superuser": tokenInfo['isAdmin']
		}

@ns.route('/authorize')
class Authorize(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@api.expect(swagger_service.mqttAuthorizeData)
	def post(self):
		username = api.payload['username']
		topic = api.payload['topic']
		action = api.payload['action']

		allow = False

		userOk = False
		mqttUser = username == settings_service.getMqttUsername()
		if mqttUser:
			userOk = True
		else:
			try:
				user_service.findUser(username)
				userOk = True
			except:
				pass

		if userOk:
			topicOk = False
			if (not mqttUser and action == 'subscribe') or (mqttUser and action == 'publish'):
				topicOk = re.search('^out/datasets/[^/]+/.*', topic) is not None # push topic: out/datasets/d1/nodes/n1/sensors/s1/readings
			elif (not mqttUser and action == 'publish') or (mqttUser and action == 'subscribe'):
				inTopics = [
					'^in/datasets/[^/]+/nodes/[^/]+/sensors/[^/]+/readings',
					'^in/datasets/[^/]+/nodes/[^/]+/readings',
					'^in/datasets/[^/]+/readings'
				]
				for inTopic in inTopics:
					topicOk = re.search(inTopic, topic) is not None
					if topicOk:
						break

			if topicOk:
				if mqttUser:
					allow = True
				else:
					datasetName = topic.split('/')[2]
					auth = {
						'username': username
					}
					try:
						finder.findDataset(auth, datasetName, create=(action == 'publish'))
						allow = True
					except:
						pass

		return {
			"result": 'allow' if allow else 'ignore'
		}
