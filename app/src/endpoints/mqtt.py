from flask_restx import Resource
from flask_restx import abort

import re

from api import api
from services import finder, swagger_service, settings_service, token_service, user_service

ns = api.namespace('mqtt', description='MQ broker endpoints')

# Called by the NanoMQ broker (see docker/rootfs/etc/nanomq.conf), which allows on status 200 and denies on anything else.

@ns.route('/authenticate')
class Authenticate(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Allowed')
	@ns.response(403, 'Denied')
	@api.expect(swagger_service.mqttAuthenticateData)
	def post(self):
		username = api.payload['username']
		password = api.payload['password']

		allow = False

		if username == settings_service.getMqttUsername():
			if password == settings_service.getMqttPassword():
				allow = True
		elif token_service.getMqttAuth(username, password):
			# users log in with a token as password, which must be their own since topic permissions are checked by username alone
			allow = True

		if not allow:
			abort(403, 'Denied')
		return 'Allowed'

@ns.route('/authorize')
class Authorize(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Allowed')
	@ns.response(403, 'Denied')
	@api.expect(swagger_service.mqttAuthorizeData)
	def post(self):
		username = api.payload['username']
		action = 'subscribe' if api.payload['access'] == '1' else 'publish'
		# all topics of a subscribe request are checked at once, joined by ','
		topics = [re.sub('^\\$share/[^/]+/', '', topic) for topic in api.payload['topic'].split(',')]

		if not all(isTopicAllowed(username, topic, action) for topic in topics):
			abort(403, 'Denied')
		return 'Allowed'

def isTopicAllowed(username, topic, action):
	if action == 'publish' and topic.startswith('$SYS/brokers/client_status/'):
		return True # NanoMQ's connect events are published in the client's name, but no one can subscribe to them

	userOk = False
	mqttUser = username == settings_service.getMqttUsername()
	if mqttUser:
		userOk = True
	else:
		try:
			user = user_service.findUser(username)
			# also stops clients that are already connected, when non-admin login is turned off
			userOk = settings_service.isLoginAllowed(user['is_admin'])
		except:
			pass

	if not userOk:
		return False

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

	if not topicOk:
		return False

	if mqttUser:
		return True

	datasetName = topic.split('/')[2]
	auth = {
		'username': username
	}
	try:
		finder.findDataset(auth, datasetName, create=(action == 'publish'))
		return True
	except:
		return False
